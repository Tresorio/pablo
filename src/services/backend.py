"""Tresorio's only interace with operators"""

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
import tempfile

import bpy
import time
import pathlib
from src.ui.popup import popup, alert, notif
from src.operators.logout import logout
from src.services.platform import Platform
from src.utils.decompress import decompress_rendering_results, get_extract_path
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
from src.utils.open_image import open_image

from src.services.pack_scene import pack_scene

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


def get_farms(rendering_mode: str, number_of_frames: int) -> None:
    token = bpy.context.window_manager.tresorio_user_props.token

    future = _get_farms(token, rendering_mode, number_of_frames)
    asyncio.ensure_future(future)

def new_upload(path: str, project_name: str) -> None:
    """Upload a new blend file"""

    token = bpy.context.window_manager.tresorio_user_props.token

    future = _new_upload(token, path, project_name)
    asyncio.ensure_future(future)


def pack_project(path: str) -> None:
    """Pack project"""

    future = _pack_project(path)
    asyncio.ensure_future(future)


def resume_render(render, farm_index) -> None:
    """Resume an already existing render"""

    token = bpy.context.window_manager.tresorio_user_props.token

    future = _resume_render(token, render, farm_index)
    asyncio.ensure_future(future)


def new_render() -> None:
    """Create and launch a new render"""
    props = bpy.context.scene.tresorio_render_form
    render_type = get_render_type()

    starting_frame = bpy.context.scene.frame_start
    ending_frame = bpy.context.scene.frame_end
    if render_type == RenderTypes.FRAME:
        starting_frame = bpy.context.scene.frame_current
        ending_frame = bpy.context.scene.frame_current

    project_name = bpy.context.scene.tresorio_render_form.project_name

    launch_render = {
        'name': props.rendering_name,
        'engine': props.render_engines_list,
        'outputFormat': props.output_formats_list,
        'mode': bpy.context.window_manager.tresorio_user_props.rendering_mode,
        'farmIndex': bpy.context.window_manager.tresorio_farm_props_index,
        'autoTileSize': props.auto_tile_size,
        'useOptix': props.use_optix,
        'startingFrame': starting_frame,
        'endingFrame': ending_frame,
        'projectName': project_name
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

    scene = bpy.data.filepath
    if bpy.context.scene.tresorio_render_form.project_name == '':
        if scene == '':
            bpy.context.scene.tresorio_render_form.project_name = TRADUCTOR['field']['default_project_name'][CONFIG_LANG]
        else:
            bpy.context.scene.tresorio_render_form.project_name = os.path.splitext(os.path.basename(scene))[0].capitalize()
    if bpy.context.scene.tresorio_render_form.project_folder == '':
        if scene == '':
            bpy.context.scene.tresorio_render_form.project_folder = tempfile.gettempdir()
        else:
            bpy.context.scene.tresorio_render_form.project_folder = os.path.dirname(scene)

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
                     render_name: str,
                     decompress_results: bool = False,
                     open_on_download: bool = False
                     ) -> None:
    try:
        with SyncNas() as nas:
            zfilepath = render_result_path
            extract_path = get_extract_path(zfilepath)
            for frag in fragments:
                nas.url = frag['ip']
                res = nas.download(frag['jwt'], folder='')
                with open(zfilepath, 'wb') as file:
                    shutil.copyfileobj(res.raw, file)
                if decompress_results:
                    decompress_rendering_results(zfilepath, extract_path)
        if open_on_download:
            # Open the outputs directory if there is no error, else base directory
            if render_details['status'] != RenderStatus.ERROR:
                open_path = os.path.join(extract_path, 'outputs', 'frames')
                if not os.path.isdir(open_path):
                    open_path = ""
            else:
                open_path = ""
            abs_open_path = os.path.join(extract_path, open_path)
            open_image(abs_open_path)

        UPDATE_QUEUE.put(('finished_download', render_details['id']))
    except Exception as err:
        BACKEND_LOGGER.error(err)
        UPDATE_QUEUE.put(('finished_download', render_details['id']))
        raise


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
            render.name,
            decompress_results,
            open_on_dl,
        )
        render.downloading = True
        await loop.run_in_executor(None, download)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        UPDATE_QUEUE.put(('finished_download', render_details['id']))
        alert(TRADUCTOR['notif']['err_download_results']
              [CONFIG_LANG])


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


def update_upload_percent(value: float):
    render_form = bpy.context.scene.tresorio_render_form
    render_form.upload_percent = value


def update_finished_upload(dummy):
    report_props = bpy.context.window_manager.tresorio_report_props
    render_form = bpy.context.scene.tresorio_render_form
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

async def _pack_project(path: str) -> Coroutine:
    bpy.context.window_manager.tresorio_report_props.packing_textures = True
    try:
        pack_scene(path)
        notif(TRADUCTOR['notif']['exported'][CONFIG_LANG].format(path))
    except Exception as e:
        print(e)
        alert(str(e))
        alert(TRADUCTOR['notif']['cant_pack_textures'][CONFIG_LANG])
    finally:
        bpy.context.window_manager.tresorio_report_props.packing_textures = False


async def _new_upload(token: str, path: str, project_name: str) -> Coroutine:
    """This function upload a new .blend file"""

    render_form = bpy.context.scene.tresorio_render_form
    render_info = None

    print("Uploading", path)
    bpy.context.window_manager.tresorio_report_props.uploading_blend_file = True

    try:
        async with Platform() as plt:
            render_info = await plt.req_create_render(token, os.path.getsize(path), project_name, jsonify=True)
            bpy.context.scene.tresorio_render_form.project_id = render_info['id']
        try:
            await _update_list_renderings(token)
        except Exception:
            pass
        bpy.context.window_manager.tresorio_renders_list_index = 0

        for dirname, dirnames, filenames in os.walk(path):
            # for subdirname in dirnames:
            #     print(os.path.relpath(os.path.join(dirname, subdirname), path))

            for filename in filenames:
                abspath = os.path.join(dirname, filename)
                relpath = pathlib.PurePosixPath(pathlib.Path(os.path.relpath(abspath, path)))
                print("Uploading", relpath)
                bpy.context.scene.tresorio_render_form.file_uploading = os.path.basename(abspath)
                loop = asyncio.get_running_loop()
                upload = functools.partial(
                    force_sync(_upload_blend_file_async), abspath, relpath, render_info)
                await loop.run_in_executor(None, upload)

    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup_msg = TRADUCTOR['notif']['err_upl_blendfile'][CONFIG_LANG]
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
            if err.status == HTTPStatus.SERVICE_UNAVAILABLE:
                popup_msg = TRADUCTOR['notif']['not_enough_servers'][CONFIG_LANG]
        alert(popup_msg)
        return
    finally:
        bpy.context.scene.tresorio_render_form.upload_percent = 0.0
        bpy.context.window_manager.tresorio_report_props.uploading_blend_file = False

async def _get_farms(
    token: str,
    rendering_mode: str,
    number_of_frames: int
) -> Coroutine:
    try:
        async with Platform() as plt:
            farms = await plt.req_get_farms(token, {
                'mode': rendering_mode,
                'numberOfFrames': number_of_frames
            }, jsonify=True)
            if len(farms) == 0:
                bpy.context.window_manager.tresorio_user_props.is_launching_rendering = False
                BACKEND_LOGGER.error("Empty response from server while getting farms")
                alert(TRADUCTOR['notif']['something_went_wrong'][CONFIG_LANG])
                return
            for farm in farms:
                item = bpy.context.window_manager.tresorio_farm_props.add()
                item.cost = farm["resources"]["cost"]
                item.gpu = farm["resources"]["gpu"]
                item.cpu = farm["resources"]["vcpu"]
                item.ram = farm["resources"]["ram"]
                item.is_available = farm["isAvailable"]
                item.units_per_farmer = farm["farmer"]["units"]
                item.number_of_farmers = farm["numberOfFarmers"]
    except Exception as err:
        bpy.context.window_manager.tresorio_user_props.is_launching_rendering = False
        BACKEND_LOGGER.error(err)
        alert(TRADUCTOR['notif']['something_went_wrong'][CONFIG_LANG])


async def _resume_render(token: str,
                        render,
                        farm_index: int
                        ) -> Coroutine:
    """Resume rendering"""

    try:
        async with Platform() as plt:
            await plt.req_resume_render(token, render.id, farm_index, jsonify=True)
            await _update_list_renderings(token)
            notif(TRADUCTOR['notif']['rendering_resumed'][CONFIG_LANG].format(render.name))
            bpy.context.window_manager.tresorio_user_settings_props.show_selected_render = True
    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup_msg = TRADUCTOR['notif']['err_launch_render'][CONFIG_LANG]
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
            if err.status == HTTPStatus.FORBIDDEN:
                popup_msg = TRADUCTOR['notif']['not_enough_credits'][CONFIG_LANG]
            elif err.status == HTTPStatus.SERVICE_UNAVAILABLE:
                alert(TRADUCTOR['notif']['rendering_failed'][CONFIG_LANG].format(render.name.capitalize()), subtitle=TRADUCTOR['notif']['not_enough_servers'][CONFIG_LANG])
                return
            elif err.status == HTTPStatus.NOT_FOUND:
                popup_msg = TRADUCTOR['notif']['no_scene'][CONFIG_LANG].format(render.project_name.capitalize())

        alert(TRADUCTOR['notif']['rendering_failed'][CONFIG_LANG].format(render.name.capitalize()) + popup_msg)


async def _new_render(token: str,
                      launch_render: Dict[str, Any]
                      ) -> Coroutine:
    """This function creates a new render and launches it."""

    render_form = bpy.context.scene.tresorio_render_form

    try:
        async with Platform() as plt:
            launch_render['projectId'] = render_form.project_id
            await plt.req_launch_render(token, launch_render, jsonify=True)
            await _update_list_renderings(token)
            notif(TRADUCTOR['notif']['rendering_launched'][CONFIG_LANG].format(render_form.rendering_name.capitalize(), render_form.project_name.capitalize()))
            bpy.context.window_manager.tresorio_renders_list_index = 0
            bpy.context.window_manager.tresorio_user_settings_props.show_selected_render = True
    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup_msg = TRADUCTOR['notif']['err_launch_render'][CONFIG_LANG]
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
            if err.status == HTTPStatus.FORBIDDEN:
                popup_msg = TRADUCTOR['notif']['not_enough_credits'][CONFIG_LANG]
            elif err.status == HTTPStatus.SERVICE_UNAVAILABLE:
                alert(TRADUCTOR['notif']['rendering_failed'][CONFIG_LANG].format(render_form.rendering_name.capitalize()), subtitle=TRADUCTOR['notif']['not_enough_servers'][CONFIG_LANG])
                return
            elif err.status == HTTPStatus.CONFLICT:
                popup_msg = TRADUCTOR['notif']['render_name_already_taken'][CONFIG_LANG].format(
                    render_form.rendering_name)
            elif err.status == HTTPStatus.NOT_FOUND:
                popup_msg = TRADUCTOR['notif']['no_scene'][CONFIG_LANG].format(render_form.project_name.capitalize())
            elif err.status == HTTPStatus.BAD_REQUEST:
                popup_msg = TRADUCTOR['notif']['wrong_name'][CONFIG_LANG]
        alert(TRADUCTOR['notif']['rendering_failed'][CONFIG_LANG].format(render_form.rendering_name.capitalize()) + popup_msg)

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
        alert(TRADUCTOR['notif']['err_stop_render'][CONFIG_LANG])
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
        alert(TRADUCTOR['notif']['err_delete_render'][CONFIG_LANG])


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


async def _upload_blend_file_async(filepath: str,
                                   relpath: str,
                                   render_info: Dict[str, Any]
                                   ) -> Coroutine:
    """Upload the blend file on a Nas

    Args:
        blendfile: Filepath of the blender file
        render_info: information about the render linked to the blend file
    """
    async with AsyncNas(render_info['ip']) as nas:
        with PercentReader(filepath, update_queue=UPDATE_QUEUE) as file:
            return await nas.upload_content(render_info['jwt'],
                                            relpath,
                                            file)


# CALLBACKS--------------------------------------------------------------------


def _fill_render_details(render: TresorioRendersDetailsProps,
                         res: Dict[str, Any],
                         is_new: bool = False
                         ) -> None:
    render.id = res['id']
    try:
        render.project_name = res['projectName']
    except Exception as e:
        pass
    render.name = res['name']
    render.cpu = res['vcpu']
    render.gpu = res['gpu']
    render.ram = res['ram']
    render.cost = res['cost']
    render.total_cost = res['totalCost']
    render.engine = res['engine']
    render.type = res['renderType']
    render.output_format = res['outputFormat']
    render.status = res['status']
    render.total_frames = res['numberOfFrames']
    render.rendered_frames = res['finishedFrames']
    render.progression = res['progression']
    render.number_of_fragments = res['fragmentCount']
    render.uptime = res['uptime']
    render.mode = res['mode']

def _add_renders_details_prop(res: Dict[str, Any]) -> None:
    render = bpy.context.window_manager.tresorio_renders_details.add()
    _fill_render_details(render, res, is_new=True)


def _get_user_info_callback(res: ClientResponse) -> None:
    bpy.context.window_manager.tresorio_user_props.total_credits = res['credits']
