"""Tresorio's only interace with operators"""

from zipfile import ZipFile
from http import HTTPStatus
from datetime import datetime
from typing import Dict, Any, List
from collections.abc import Coroutine
import io
import os
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
from src.properties.renders import TresorioRendersDetailsProps
from bundle_modules.aiohttp import ClientResponseError, ClientResponse

# pylint: disable=assignment-from-no-return,assignment-from-none,unexpected-keyword-arg

WM = bpy.context.window_manager


def logout_if_unauthorized(err: ClientResponseError) -> None:
    """Log the user out if its token became invalid

    Arg:
        err: The error that appeared doing a request to the backend of Tresorio
    """
    if err.status == HTTPStatus.UNAUTHORIZED:
        logout(bpy.context)
        popup(TRADUCTOR['notif']['expired_session'][CONFIG_LANG], icon='ERROR')


def new_render() -> None:
    """Create and launch a new render"""
    props = bpy.context.scene.tresorio_render_form
    render_type = get_render_type()
    number_of_frames = 1

    if render_type == RenderTypes.ANIMATION:
        number_of_frames = 1 + bpy.context.scene.frame_end - bpy.context.scene.frame_start

    create_render = {
        'name': props.rendering_name,
        'engine': props.render_engines_list,
        'outputFormat': props.output_formats_list,
        'timeout': props.timeout,
        'farm': props.render_pack,
        'renderType': render_type,
        'size': os.path.getsize(bpy.data.filepath),
        'numberFarmers': props.nb_farmers,
        'numberOfFrames': number_of_frames,
        'autoTileSize': props.auto_tile_size,
        'farmType': props.farm_type,
    }
    launch_render = {
        'currentFrame': bpy.context.scene.frame_current,
        'startingFrame': bpy.context.scene.frame_start,
        'endingFrame': bpy.context.scene.frame_end,
    }
    token = WM.tresorio_user_props.token

    future = _new_render(token, create_render, launch_render)
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
        ... time.sleep(5)
        ... uptime = get_uptime(start) # 5
    """
    return datetime.utcnow().timestamp() - created_at


def delete_render(render_id: str,
                  index: int
                  ) -> None:
    """Delete a render

    Args:
        render_id: The unique id of the render to delete
        index: the index in the blender renders list of the render to delete
    """
    token = WM.tresorio_user_props.token
    future = _delete_render(token, render_id, index)
    asyncio.ensure_future(future)


def stop_render(render: TresorioRendersDetailsProps) -> None:
    """Stop a render

    Arg:
        render: The render to stop
    """
    token = WM.tresorio_user_props.token
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
    token = WM.tresorio_user_props.token
    future = _download_render_results(token, render_id, render_result_path)
    asyncio.ensure_future(future)


def update_list_renderings():
    """Update all the renderings"""
    token = WM.tresorio_user_props.token
    future = _update_list_renderings(token)
    asyncio.ensure_future(future)


def update_rendering(render: TresorioRendersDetailsProps):
    """Update a specific rendering

    Arg:
        render: The render to update
    """
    token = WM.tresorio_user_props.token
    future = _update_rendering(render, token)
    asyncio.ensure_future(future)


def delete_all_renders():
    """Delete all the renders"""
    token = WM.tresorio_user_props.token
    future = _delete_all_renders(token)
    asyncio.ensure_future(future)


def _download_frames(fragments: List[Dict[str, Any]],
                     render_result_path: str,
                     render_details: Dict[str, Any],
                     render: TresorioRendersDetailsProps
                     ) -> None:
    filepath = None
    user_settings = WM.tresorio_user_settings_props
    ext = render_details['outputFormat'].lower()
    with SyncNas() as nas:
        for frag in fragments:
            nas.url = frag['ip']
            zip_bytes = io.BytesIO(
                nas.download_project(frag['id'], frag['jwt'], read=True))
            with ZipFile(zip_bytes) as zipf:
                frames = list(filter(
                    lambda x: x.startswith('artifacts/') and x != 'artifacts/',
                    zipf.namelist()
                ))
                for frame in frames:
                    zip_bytes = zipf.read(frame)
                    filename = f'%s_{os.path.basename(frame)}.{ext}' % render['name']
                    filepath = os.path.join(render_result_path, filename)
                    with open(filepath, 'wb') as file:
                        file.write(zip_bytes)
                        BACKEND_LOGGER.debug(f'Wrote file {filepath}')
    if filepath is not None and user_settings.open_image_on_download:
        open_image(filepath)


def update_renderings_uptime() -> None:
    """Update the uptime of all non finished renders"""
    renders = WM.tresorio_renders_details
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
        fragments = render_details['fragments']
        loop = asyncio.get_running_loop()
        download = functools.partial(
            _download_frames, fragments, render_result_path, render_details, render
        )
        render.downloading = True
        await loop.run_in_executor(None, download)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup(TRADUCTOR['notif']['err_download_results']
              [CONFIG_LANG], icon='ERROR')
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
    finally:
        render.downloading = False


async def _update_user_info(token: str) -> Coroutine:
    async with Platform() as plt:
        try:
            res_user_info = await plt.req_get_user_info(token, jsonify=True)
            _get_user_info_callback(res_user_info)
        except Exception as err:
            BACKEND_LOGGER.error(err)
            popup(TRADUCTOR['notif']['err_acc_info']
                  [CONFIG_LANG], icon='ERROR')
            if isinstance(err, ClientResponseError):
                logout_if_unauthorized(err)


async def _update_renderpacks_info(token: str) -> Coroutine:
    async with Platform() as plt:
        try:
            res_renderpacks = await plt.req_get_renderpacks(token, jsonify=True)
            _get_renderpacks_callback(res_renderpacks)
        except Exception as err:
            BACKEND_LOGGER.error(err)
            popup(TRADUCTOR['notif']
                  ['err_renderpacks'][CONFIG_LANG], icon='ERROR')
            if isinstance(err, ClientResponseError):
                logout_if_unauthorized(err)
            bpy.context.scene.tresorio_render_form.render_pack = ''


async def _refresh_loop(token: str) -> Coroutine:
    while WM.tresorio_user_props.is_logged:
        await _update_user_info(token)
        await _update_list_renderings(token)
        for _ in range(5):
            update_renderings_uptime()
            await asyncio.sleep(1)


async def _connect_to_tresorio(data: Dict[str, str]) -> Coroutine:
    async with Platform() as plt:
        try:
            bpy.context.scene.tresorio_report_props.login_in = True
            res_connect = await plt.req_connect_to_tresorio(data, jsonify=True)
            _connect_to_tresorio_callback(res_connect)
        except Exception as err:
            BACKEND_LOGGER.error(err)
            if isinstance(err, ClientResponseError):
                if err.status == HTTPStatus.UNAUTHORIZED:
                    popup(TRADUCTOR['notif']['invalid_login'][CONFIG_LANG],
                          icon='ERROR')
            else:
                popup(TRADUCTOR['notif']
                      ['err_connection'][CONFIG_LANG], icon='ERROR')
        else:
            await _update_renderpacks_info(res_connect['token'])
            await _refresh_loop(res_connect['token'])
        finally:
            bpy.context.scene.tresorio_report_props.login_in = False


async def _update_list_renderings(token: str) -> Coroutine:
    try:
        async with Platform() as plt:
            res_renders = await plt.req_list_renderings_details(token, jsonify=True)
            WM.property_unset('tresorio_renders_details')
            for res in res_renders:
                render = WM.tresorio_renders_details.add()
                _fill_render_details(render, res, is_new=True)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
        else:
            popup(TRADUCTOR['notif']['err_renders'][CONFIG_LANG], icon='ERROR')


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


async def _new_render(token: str,
                      create_render: Dict[str, Any],
                      launch_render: Dict[str, Any]
                      ) -> Coroutine:
    """This function creates a new render, packs the textures, uploads the blend
       file, unpacks the textures, and finally launches the rendering."""

    blendfile = bpy.data.filepath
    render_form = bpy.context.scene.tresorio_render_form
    render_info = None

    try:
        if render_form.pack_textures:
            bpy.context.scene.tresorio_report_props.packing_textures = True
            bpy.ops.file.pack_all()
            bpy.ops.wm.save_as_mainfile(filepath=blendfile)
    except RuntimeError as err:
        BACKEND_LOGGER.error(err)
        popup(TRADUCTOR['notif']['cant_pack_textures']
              [CONFIG_LANG], icon='ERROR')
        return
    finally:
        bpy.context.scene.tresorio_report_props.packing_textures = False

    try:
        async with Platform() as plt:
            bpy.context.scene.tresorio_report_props.creating_render = True
            render_info = await plt.req_create_render(token, create_render, jsonify=True)
        await _update_list_renderings(token)
        WM.tresorio_renders_list_index = 0
        loop = asyncio.get_running_loop()
        upload = functools.partial(
            force_sync(_upload_blend_file_async), blendfile, render_info)
        await loop.run_in_executor(None, upload)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup_msg = TRADUCTOR['notif']['err_upl_blendfile'][CONFIG_LANG]
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
            if err.status == HTTPStatus.FORBIDDEN:
                popup_msg = TRADUCTOR['notif']['not_enough_credits'][CONFIG_LANG]
            elif err.status == HTTPStatus.SERVICE_UNAVAILABLE:
                popup_msg = TRADUCTOR['notif']['not_enough_servers'][CONFIG_LANG]
            elif err.status == HTTPStatus.CONFLICT:
                popup_msg = TRADUCTOR['notif']['render_name_already_taken'][CONFIG_LANG].format(
                    render_form.rendering_name)
        if render_info is not None:
            await _delete_render(token, render_info['id'], 0)
        popup(msg=popup_msg, icon='ERROR')
        return
    finally:
        bpy.context.scene.tresorio_report_props.creating_render = False
        bpy.context.scene.tresorio_report_props.uploading_blend_file = False
        try:
            if render_form.pack_textures:
                bpy.context.scene.tresorio_report_props.unpacking_textures = True
                bpy.ops.file.unpack_all()
                bpy.ops.wm.save_as_mainfile(filepath=blendfile)
        except RuntimeError as err:
            BACKEND_LOGGER.error(err)
            popup(TRADUCTOR['notif']['cant_unpack_textures']
                  [CONFIG_LANG], icon='ERROR')
        finally:
            bpy.context.scene.tresorio_report_props.unpacking_textures = False

    try:
        async with Platform() as plt:
            await plt.req_launch_render(token, render_info['id'], launch_render, jsonify=True)
            await _update_list_renderings(token)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup_msg = TRADUCTOR['notif']['err_launch_render'][CONFIG_LANG]
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
            if err.status == HTTPStatus.SERVICE_UNAVAILABLE:
                popup_msg = TRADUCTOR['notif']['not_enough_servers'][CONFIG_LANG]
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
                         index: int
                         ) -> Coroutine:
    try:
        async with Platform() as plt:
            await plt.req_delete_render(token, render_id)
            if index >= 0:
                WM.tresorio_renders_details.remove(index)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
        popup(TRADUCTOR['notif']['err_delete_render'][CONFIG_LANG],
              icon='ERROR')


async def _delete_all_renders(token: str) -> Coroutine:
    try:
        bpy.context.scene.tresorio_report_props.deleting_all_renders = True
        async with Platform() as plt:
            renders = await plt.req_list_renderings_details(token, jsonify=True)
            for render in renders:
                await _delete_render(token, render['id'], 0)
        await _update_list_renderings(token)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
    finally:
        bpy.context.scene.tresorio_report_props.deleting_all_renders = False


def update_upload_percent(percent: float) -> None:
    """Update the upload percent of the file

    Arg:
        percent: Advancement (0-100) of the file upload
    """
    bpy.context.scene.tresorio_render_form.upload_percent = percent


async def _upload_blend_file_async(blendfile: str,
                                   render_info: Dict[str, Any]
                                   ) -> Coroutine:
    """Upload the blend file on a Nas

    Args:
        blendfile: Filepath of the blender file
        render_info: information about the render linked to the blend file
    """
    bpy.context.scene.tresorio_report_props.uploading_blend_file = True
    async with AsyncNas(render_info['ip']) as nas:
        BACKEND_LOGGER.debug(f'Uploading for render ' + render_info['id'])
        with PercentReader(blendfile, update_upload_percent) as file:
            return await nas.upload_content(render_info['id'],
                                            render_info['jwt'],
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
    render.number_farmers = res['numberFarmers']
    render.progression = res['progression']
    if is_new and render.status != RenderStatus.FINISHED:
        render.created_at = datetime.strptime(
            res['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
        render.uptime = get_uptime(render.created_at)
    if res['status'] == RenderStatus.FINISHED:
        render.uptime = res['uptime']


def _add_renders_details_prop(res: Dict[str, Any]) -> None:
    render = WM.tresorio_renders_details.add()
    _fill_render_details(render, res, is_new=True)


def _get_renderpacks_callback(res: ClientResponse) -> None:
    WM.property_unset('tresorio_render_packs')
    last_selected = bpy.context.scene.tresorio_render_form.last_renderpack_selected
    for i, pack in enumerate(res):
        new_pack = WM.tresorio_render_packs.add()
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
    WM.tresorio_user_props.total_credits = res['credits']


def _connect_to_tresorio_callback(res: ClientResponse) -> None:
    WM.tresorio_user_props.token = res['token']
    WM.tresorio_user_props.is_logged = True
