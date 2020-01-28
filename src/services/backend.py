"""Tresorio's only interace with operators"""

from zipfile import ZipFile
from http import HTTPStatus
from datetime import datetime
from typing import Dict, Any, List
from collections.abc import Coroutine
from queue import Queue
import io
import os
import shutil
import asyncio
import functools

import bpy
from src.ui.popup import popup
from src.operators.logout import logout
from src.services.platform import Platform
from src.utils.open_image import open_image
from src.utils.force_sync import force_sync
from src.services.nas import AsyncNas, SyncNas
from src.services.loggers import BACKEND_LOGGER
from src.utils.percent_reader import PercentReader
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.operators.async_loop import ensure_async_loop
from src.config.enums import RenderStatus, RenderTypes
from src.properties.render_form import get_render_type
from src.properties.render_packs import get_selected_pack
from src.properties.renders import TresorioRendersDetailsProps
from bundle_modules.aiohttp import ClientResponseError, ClientResponse

# pylint: disable=assignment-from-no-return,assignment-from-none,unexpected-keyword-arg
UPDATE_QUEUE = Queue()


def logout_if_unauthorized(err: ClientResponseError) -> None:
    """Log the user out if its token became invalid

    Arg:
        err: The error that appeared doing a request to the backend of Tresorio
    """
    if err.status == HTTPStatus.UNAUTHORIZED:
        logout(bpy.context)
        popup(TRADUCTOR['notif']['expired_session'][CONFIG_LANG], icon='ERROR')


def new_upload() -> None:
    """Upload a new blend file"""

    token = bpy.context.window_manager.tresorio_user_props.token

    future = _new_upload(token)
    asyncio.ensure_future(future)


def new_render() -> None:
    """Create and launch a new render"""
    props = bpy.context.scene.tresorio_render_form
    render_type = get_render_type()
    number_of_frames = 1

    if render_type == RenderTypes.ANIMATION:
        number_of_frames = 1 + bpy.context.scene.frame_end - bpy.context.scene.frame_start

    # Deactivating Optix for now, systematically send False to Gandalf
    use_optix = False
    # use_optix = props.use_optix
    # curr_pack = get_selected_pack()
    # if props.render_engines_list != 'CYCLES' or curr_pack is not None and curr_pack.gpu <= 0:
        # use_optix = False

    launch_render = {
        'name': props.rendering_name,
        'engine': props.render_engines_list,
        'outputFormat': props.output_formats_list,
        'timeout': props.timeout,
        'farm': props.render_pack,
        'renderType': render_type,
        'numberOfFarmers': props.nb_farmers,
        'numberOfFrames': number_of_frames,
        'autoTileSize': props.auto_tile_size,
        'useOptix': use_optix,
        'currentFrame': bpy.context.scene.frame_current,
        'startingFrame': bpy.context.scene.frame_start,
        'endingFrame': bpy.context.scene.frame_end,
    }
    token = bpy.context.window_manager.tresorio_user_props.token

    future = _new_render(token, launch_render)
    asyncio.ensure_future(future)


def connect_to_tresorio(email: str,
                        password: str
                        ) -> None:
    """Connects the user to Tresorio and fetch required data"""
    credentials = {
        'email': email,
        'password': password
    }

    future = _connect_to_tresorio(credentials)
    asyncio.ensure_future(future)
    ensure_async_loop()


def get_uptime(created_at: int) -> int:
    """Calculates a time difference using UTC time

    Arg:
        created_at: Creation date in unix seconds (UTC)

    Example:

        >>> start = utc.now()
        ... time.sleep(2)
        ... uptime = get_uptime(start) # 2
    """
    return datetime.utcnow().timestamp() - created_at


def delete_render(render_id: str) -> None:
    """Delete a render

    Args:
        render_id: The unique id of the render to delete
        index: the index in the blender renders list of the render to delete
    """
    token = bpy.context.window_manager.tresorio_user_props.token
    future = _delete_render(token, render_id)
    asyncio.ensure_future(future)


def stop_render(render: TresorioRendersDetailsProps) -> None:
    """Stop a render

    Arg:
        render: The render to stop
    """
    token = bpy.context.window_manager.tresorio_user_props.token
    future = _stop_render(token, render)
    asyncio.ensure_future(future)


def download_render_results(render_id: str,
                            render_result_path: str
                            ) -> None:
    """Download the results of a render

    Args:
        render_id: The unique id of the render to target
        render_result_path: the filepath where to write the downloaded results
    """
    token = bpy.context.window_manager.tresorio_user_props.token
    future = _download_render_results(token, render_id, render_result_path)
    asyncio.ensure_future(future)


def update_list_renderings():
    """Update all the renderings"""
    token = bpy.context.window_manager.tresorio_user_props.token
    future = _update_list_renderings(token)
    asyncio.ensure_future(future)


def delete_all_renders():
    """Delete all the renders"""
    token = bpy.context.window_manager.tresorio_user_props.token
    future = _delete_all_renders(token)
    asyncio.ensure_future(future)


def _download_frames(fragments: List[Dict[str, Any]],
                     render_result_path: str,
                     render_details: Dict[str, Any],
                     decompress_results: bool = False,
                     open_on_download: bool = False,
                     ) -> None:
    try:
        with SyncNas() as nas:
            for frag in fragments:
                nas.url = frag['ip']
                res = nas.download(frag['jwt'], folder='artifacts')
                zfilepath = render_result_path
                with open(zfilepath, 'wb') as file:
                    shutil.copyfileobj(res.raw, file)
                if decompress_results:
                    with ZipFile(zfilepath) as zfile:
                        extract_path = os.path.dirname(render_result_path)
                        zfile.extractall(path=extract_path)
                        os.remove(zfilepath)
                        if open_on_download:
                            image = zfile.namelist()[0]
                            image_path = os.path.join(extract_path, image)
                            open_image(image_path)
        UPDATE_QUEUE.put(('finished_download', render_details['id']))
    except Exception as err:
        BACKEND_LOGGER.error(err)
        UPDATE_QUEUE.put(('finished_download', render_details['id']))


def update_renderings_uptime() -> None:
    """Update the uptime of all non finished renders"""
    renders = bpy.context.window_manager.tresorio_renders_details
    for render in renders:
        if render.status != RenderStatus.FINISHED:
            render.uptime = get_uptime(render.created_at)


# ASYNC CORE-------------------------------------------------------------------

async def _download_render_results(token: str,
                                   render: TresorioRendersDetailsProps,
                                   render_result_path: str
                                   ) -> Coroutine:
    try:
        async with Platform() as plt:
            render_details = await plt.req_get_rendering_details(token, render.id, jsonify=True)
        user_settings = bpy.context.window_manager.tresorio_user_settings_props
        fragments = render_details['fragments']
        loop = asyncio.get_running_loop()
        open_on_dl = user_settings.open_image_on_download
        decompress_results = user_settings.decompress_results
        download = functools.partial(
            _download_frames,
            fragments,
            render_result_path,
            render_details,
            decompress_results,
            open_on_dl
        )
        render.downloading = True
        await loop.run_in_executor(None, download)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        UPDATE_QUEUE.put(('finished_download', render_details['id']))
        popup(TRADUCTOR['notif']['err_download_results']
              [CONFIG_LANG], icon='ERROR')


async def _update_user_info(token: str,
                            silence_errors: bool = False
                            ) -> Coroutine:
    async with Platform() as plt:
        try:
            res_user_info = await plt.req_get_user_info(token, jsonify=True)
            _get_user_info_callback(res_user_info)
        except Exception as err:
            BACKEND_LOGGER.error(err)
            if isinstance(err, ClientResponseError):
                logout_if_unauthorized(err)
            elif silence_errors is False:
                popup(TRADUCTOR['notif']['err_acc_info']
                      [CONFIG_LANG], icon='ERROR')


async def _update_renderpacks_info(token: str) -> Coroutine:
    async with Platform() as plt:
        try:
            res_renderpacks = await plt.req_get_renderpacks(token, jsonify=True)
            _get_renderpacks_callback(res_renderpacks)
        except Exception as err:
            bpy.context.scene.tresorio_render_form.render_pack = ''
            BACKEND_LOGGER.error(err)
            popup(TRADUCTOR['notif']
                  ['err_renderpacks'][CONFIG_LANG], icon='ERROR')
            if isinstance(err, ClientResponseError):
                logout_if_unauthorized(err)


def update_upload_percent(value: float):
    render_form = bpy.context.scene.tresorio_render_form
    render_form.upload_percent = value


def update_finished_upload(dummy):
    report_props = bpy.context.window_manager.tresorio_report_props
    render_form = bpy.context.scene.tresorio_render_form
    report_props.uploading_blend_file = False
    render_form.upload_percent = 0.0


def update_finished_download(render_id: str):
    renders = bpy.context.window_manager.tresorio_renders_details
    for render in renders:
        if render.id == render_id:
            render.downloading = False
            return


async def _refresh_loop(token: str) -> Coroutine:
    comms = {
        'upload_percent': update_upload_percent,
        'finished_upload': update_finished_upload,
        'finished_download': update_finished_download,
    }
    is_logged = bpy.context.window_manager.tresorio_user_props.is_logged
    while is_logged:
        await _update_user_info(token, silence_errors=True)
        await _update_list_renderings(token, silence_errors=True)
        for _ in range(20):
            while not UPDATE_QUEUE.empty():
                instruction, obj = UPDATE_QUEUE.get(block=False)
                comms[instruction](obj)
            update_renderings_uptime()
            await asyncio.sleep(0.25)
        is_logged = bpy.context.window_manager.tresorio_user_props.is_logged


async def _connect_to_tresorio(data: Dict[str, str]) -> Coroutine:
    async with Platform() as plt:
        try:
            bpy.context.window_manager.tresorio_report_props.login_in = True
            res_connect = await plt.req_connect_to_tresorio(data, jsonify=True)
            bpy.context.window_manager.tresorio_user_props.token = res_connect['token']
            bpy.context.window_manager.tresorio_user_props.is_logged = True
        except Exception as err:
            bpy.context.window_manager.tresorio_report_props.login_in = False
            BACKEND_LOGGER.error(err)
            if isinstance(err, ClientResponseError):
                if err.status == HTTPStatus.UNAUTHORIZED:
                    popup(TRADUCTOR['notif']['invalid_login'][CONFIG_LANG],
                          icon='ERROR')
            else:
                popup(TRADUCTOR['notif']
                      ['err_connection'][CONFIG_LANG], icon='ERROR')
        else:
            bpy.context.window_manager.tresorio_report_props.login_in = False
            await _update_renderpacks_info(res_connect['token'])
            await _refresh_loop(res_connect['token'])


async def _update_list_renderings(token: str,
                                  silence_errors: bool = False
                                  ) -> Coroutine:
    try:
        async with Platform() as plt:
            res_renders = await plt.req_list_renderings_details(token, jsonify=True)
            update_ui_renderings(res_renders, is_new=True)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
        elif silence_errors is False:
            popup(TRADUCTOR['notif']['err_renders'][CONFIG_LANG], icon='ERROR')


def update_ui_renderings(res_renders,
                         is_new: bool
                         ) -> None:
    renders = bpy.context.window_manager.tresorio_renders_details
    downloading = [render.id for render in renders if render.downloading]
    bpy.context.window_manager.property_unset('tresorio_renders_details')
    for res in res_renders:
        render = bpy.context.window_manager.tresorio_renders_details.add()
        _fill_render_details(render, res, is_new=is_new)
        if render.id in downloading:
            render.downloading = True


async def _update_rendering(render: TresorioRendersDetailsProps,
                            token: str
                            ) -> Coroutine:
    try:
        async with Platform() as plt:
            BACKEND_LOGGER.debug(f'Updating render {render.id}')
            render_details = await plt.req_get_rendering_details(token, render.id, jsonify=True)
            _fill_render_details(render, render_details)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup(TRADUCTOR['notif']['err_render'][CONFIG_LANG], icon='ERROR')
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)

async def _new_upload(token: str) -> Coroutine:
    """This function upload a new .blend file"""

    blendfile = bpy.data.filepath
    render_form = bpy.context.scene.tresorio_render_form
    render_info = None

    try:
        if render_form.pack_textures:
            bpy.context.window_manager.tresorio_report_props.packing_textures = True
            bpy.ops.file.pack_all()
            bpy.ops.wm.save_as_mainfile(filepath=blendfile)
    except RuntimeError as err:
        BACKEND_LOGGER.error(err)
        popup(TRADUCTOR['notif']['cant_pack_textures']
              [CONFIG_LANG], icon='ERROR')
        return
    finally:
        bpy.context.window_manager.tresorio_report_props.packing_textures = False

    try:
        async with Platform() as plt:
            bpy.context.window_manager.tresorio_report_props.creating_render = True
            render_info = await plt.req_create_render(token, os.path.getsize(bpy.data.filepath), jsonify=True)
            bpy.context.scene.tresorio_render_form.project_id = render_info['id']
        try:
            await _update_list_renderings(token)
        except Exception:
            pass
        bpy.context.window_manager.tresorio_renders_list_index = 0
        loop = asyncio.get_running_loop()
        upload = functools.partial(
            force_sync(_upload_blend_file_async), blendfile, render_info)
        bpy.context.window_manager.tresorio_report_props.uploading_blend_file = True
        await loop.run_in_executor(None, upload)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup_msg = TRADUCTOR['notif']['err_upl_blendfile'][CONFIG_LANG]
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
            if err.status == HTTPStatus.SERVICE_UNAVAILABLE:
                popup_msg = TRADUCTOR['notif']['not_enough_servers'][CONFIG_LANG]
        if render_info is not None:
            await _delete_render(token, render_info['id'])
        popup(msg=popup_msg, icon='ERROR')
        return
    finally:
        bpy.context.scene.tresorio_render_form.upload_percent = 0.0
        bpy.context.window_manager.tresorio_report_props.creating_render = False

async def _new_render(token: str,
                      launch_render: Dict[str, Any]
                      ) -> Coroutine:
    """This function creates a new render, packs the textures, uploads the blend
       file, and finally launches the rendering."""

    render_form = bpy.context.scene.tresorio_render_form

    try:
        async with Platform() as plt:
            launch_render['projectId'] = render_form.project_id
            await plt.req_launch_render(token, launch_render, jsonify=True)
            await _update_list_renderings(token)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup_msg = TRADUCTOR['notif']['err_launch_render'][CONFIG_LANG]
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
            if err.status == HTTPStatus.FORBIDDEN:
                popup_msg = TRADUCTOR['notif']['not_enough_credits'][CONFIG_LANG]
            elif err.status == HTTPStatus.SERVICE_UNAVAILABLE:
                popup_msg = TRADUCTOR['notif']['not_enough_servers'][CONFIG_LANG]
            elif err.status == HTTPStatus.CONFLICT:
                popup_msg = TRADUCTOR['notif']['render_name_already_taken'][CONFIG_LANG].format(
                    render_form.rendering_name)
            elif err.status == HTTPStatus.BAD_REQUEST:
                popup_msg = TRADUCTOR['notif']['no_scene'][CONFIG_LANG]
        popup(msg=popup_msg, icon='ERROR')

async def _stop_render(token: str,
                       render: TresorioRendersDetailsProps
                       ) -> Coroutine:
    try:
        async with Platform() as plt:
            BACKEND_LOGGER.debug(f'Stopping render {render.id}')
            await plt.req_stop_render(token, render.id, jsonify=True)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
        popup(TRADUCTOR['notif']['err_stop_render'][CONFIG_LANG], icon='ERROR')
    else:
        await _update_rendering(render, token)


async def _delete_render(token: str,
                         render_id: str,
                         ) -> Coroutine:
    try:
        async with Platform() as plt:
            renders = await plt.req_delete_render(token, render_id, jsonify=True)
            update_ui_renderings(renders, is_new=True)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
        popup(TRADUCTOR['notif']['err_delete_render'][CONFIG_LANG],
              icon='ERROR')


async def _delete_all_renders(token: str) -> Coroutine:
    try:
        bpy.context.window_manager.tresorio_report_props.deleting_all_renders = True
        async with Platform() as plt:
            renders = await plt.req_list_renderings_details(token, jsonify=True)
            for render in renders:
                await _delete_render(token, render['id'])
    except Exception as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
    finally:
        bpy.context.window_manager.tresorio_report_props.deleting_all_renders = False


async def _upload_blend_file_async(blendfile: str,
                                   render_info: Dict[str, Any]
                                   ) -> Coroutine:
    """Upload the blend file on a Nas

    Args:
        blendfile: Filepath of the blender file
        render_info: information about the render linked to the blend file
    """
    async with AsyncNas(render_info['ip']) as nas:
        with PercentReader(blendfile, update_queue=UPDATE_QUEUE) as file:
            return await nas.upload_content(render_info['jwt'],
                                            'scene.blend',
                                            file)


# CALLBACKS--------------------------------------------------------------------


def _fill_render_details(render: TresorioRendersDetailsProps,
                         res: Dict[str, Any],
                         is_new: bool = False
                         ) -> None:
    render.id = res['id']
    render.name = res['name']
    render.timeout = res['timeout']
    render.type = res['renderType']
    render.engine = res['engine']
    render.farm = res['farm']
    render.output_format = res['outputFormat']
    render.status = res['status']
    render.total_frames = res['numberOfFrames']
    render.rendered_frames = res['finishedFrames']
    render.number_farmers = res['numberOfFarmers']
    render.progression = res['progression']
    if is_new and render.status != RenderStatus.FINISHED:
        render.created_at = datetime.strptime(
            res['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
        render.uptime = get_uptime(render.created_at)
    if res['status'] == RenderStatus.FINISHED:
        render.uptime = res['uptime']


def _add_renders_details_prop(res: Dict[str, Any]) -> None:
    render = bpy.context.window_manager.tresorio_renders_details.add()
    _fill_render_details(render, res, is_new=True)


def _get_renderpacks_callback(res: ClientResponse) -> None:
    bpy.context.window_manager.property_unset('tresorio_render_packs')
    last_selected = bpy.context.scene.tresorio_render_form.last_renderpack_selected
    for i, pack in enumerate(res):
        new_pack = bpy.context.window_manager.tresorio_render_packs.add()
        new_pack.name = pack['name']
        new_pack.cost = pack['cost']
        new_pack.gpu = pack['gpu']
        new_pack.cpu = pack['vcpu']
        new_pack.ram = pack['ram']
        new_pack.description = TRADUCTOR['desc']['pack_full_description_popup'][CONFIG_LANG].format(
            new_pack.cost,
            new_pack.gpu,
            pack['gpuModel'],
            new_pack.cpu, pack['cpuModel'],
            new_pack.ram)
        if i == 0:
            new_pack.is_selected = True
            bpy.context.scene.tresorio_render_form.render_pack = pack['name']
        elif last_selected == pack['name']:
            new_pack.is_selected = True
            bpy.context.scene.tresorio_render_form.render_pack = pack['name']


def _get_user_info_callback(res: ClientResponse) -> None:
    bpy.context.window_manager.tresorio_user_props.total_credits = res['credits']
