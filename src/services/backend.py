"""Tresorio's only interace with operators"""

import io
import os
import bpy
import time
import asyncio
import functools
from zipfile import ZipFile
from http import HTTPStatus
from datetime import datetime
from src.ui.popup import popup
from urllib.parse import urljoin
from typing import Dict, Any, List
from src.operators.logout import logout
from src.utils.lockfile import Lockfile
from src.config.enums import RenderStatus
from src.services.platform import Platform
from src.utils.open_image import open_image
from src.utils.force_sync import force_sync
from src.services.nas import AsyncNas, SyncNas
from src.services.loggers import BACKEND_LOGGER
from src.utils.percent_reader import PercentReader
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.async_loop import ensure_async_loop
from src.properties.render_form import get_render_type
from bundle_modules.aiohttp import ClientResponseError, ClientResponse


WM = bpy.context.window_manager


def logout_if_unauthorized(err: Exception):
    if isinstance(err, ClientResponseError) and err.status == HTTPStatus.UNAUTHORIZED:
        logout()
        popup(TRADUCTOR['notif']['expired_session'][CONFIG_LANG], icon='ERROR')
        return True
    return False


def new_render():
    props = bpy.context.scene.tresorio_render_form
    render_type = get_render_type()
    number_of_frames = 1

    if render_type == 'ANIMATION':  # TODO enum
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


def connect_to_tresorio(email: str, password: str):
    """Connects the user to Tresorio and fetch required data"""
    bpy.context.scene.tresorio_report_props.error = False
    WM.tresorio_user_props.token = ''
    bpy.context.scene.tresorio_report_props.login_in = 1

    credentials = {
        'email': email,
        'password': password
    }

    future = _connect_to_tresorio(credentials)
    asyncio.ensure_future(future)
    ensure_async_loop()


def get_uptime(created_at: int):
    return datetime.utcnow().timestamp() - created_at


def delete_render(render_id: str, index: int):
    token = WM.tresorio_user_props.token
    future = _delete_render(token, render_id, index)
    asyncio.ensure_future(future)


def stop_render(render_id: str):
    token = WM.tresorio_user_props.token
    future = _stop_render(token, render_id)
    asyncio.ensure_future(future)


def download_render_results(render_id: str, render_result_path: str):
    token = WM.tresorio_user_props.token
    future = _download_render_results(token, render_id, render_result_path)
    asyncio.ensure_future(future)


def download_targeted_render_results(renders_result_path: str):
    token = WM.tresorio_user_props.token
    future = _download_targeted_render_results(token, renders_result_path)
    asyncio.ensure_future(future)


def delete_targeted_render_results():
    token = WM.tresorio_user_props.token
    future = _delete_targeted_renders(token)
    asyncio.ensure_future(future)


def update_list_renderings():
    bpy.context.scene.tresorio_report_props.are_renders_refreshing = True
    token = WM.tresorio_user_props.token
    future = _update_list_renderings(token)
    asyncio.ensure_future(future)


def update_rendering(render):
    bpy.context.scene.tresorio_report_props.are_renders_refreshing = True
    token = WM.tresorio_user_props.token
    future = _update_rendering(render, token)
    asyncio.ensure_future(future)


# ASYNC CORE-------------------------------------------------------------------


def _download_logs(fragments: List[Dict[str, Any]], filepath: str):
    open(filepath, 'wb').close()
    with SyncNas() as nas:
        with open(filepath, 'ab') as file:
            for frag in fragments:
                nas.url = frag['ip']
                logs = nas.download(frag['id'], 'logs.txt', read=True)
                file.write(logs)
                BACKEND_LOGGER.debug(f'Wrote logs on file {filepath}')


def _download_frames(fragments: List[Dict[str, Any]], render_result_path: str, render_details: Dict[str, Any], render, open_result: bool = True):
    ext = render_details['outputFormat'].lower()
    with SyncNas() as nas:
        for frag in fragments:
            nas.url = frag['ip']
            zip_bytes = io.BytesIO(nas.download_project(frag['id'], read=True))
            with ZipFile(zip_bytes) as zf:
                frames = list(filter(
                    lambda x: x.startswith('artifacts/') and x != 'artifacts/',
                    zf.namelist()
                ))
                for i, frame in enumerate(frames):
                    zip_bytes = zf.read(frame)
                    filename = f'%s_{os.path.basename(frame)}.{ext}' % render['name']
                    filepath = os.path.join(render_result_path, filename)
                    with open(filepath, 'wb') as fw:
                        fw.write(zip_bytes)
                        BACKEND_LOGGER.debug(f'Wrote file {filepath}')
                    if i == 0 and WM.tresorio_user_settings_props.open_image_on_download and open_result:
                        open_image(filepath)


async def _download_render_results(token: str, render, render_result_path: str, open_result: bool = True):
    try:
        async with Platform() as plt:
            BACKEND_LOGGER.debug(f'Downloading render {render.id} results')
            render_details = await plt.req_get_rendering_details(token, render.id, jsonify=True)
        fragments = render_details['fragments']
        loop = asyncio.get_running_loop()
        download = functools.partial(
            _download_frames, fragments, render_result_path, render_details, render
        )
        render.downloading = True
        await loop.run_in_executor(None, download, open_result)
    except (ClientResponseError, Exception) as err:
        BACKEND_LOGGER.error(err)
        if logout_if_unauthorized(err):
            return
        elif isinstance(err, ClientResponseError) is False:
            popup(TRADUCTOR['notif']['err_download_results']
                  [CONFIG_LANG], icon='ERROR')
    finally:
        render.downloading = False


async def _download_targeted_render_results(token: str, renders_result_path: str):
    for i, render in enumerate(WM.tresorio_renders_details):
        if render.status == RenderStatus.FINISHED and render.is_target:
            await _download_render_results(token, render, renders_result_path, open_result=(i == 0))


async def _delete_targeted_renders(token: str):
    delta = 0
    renders = WM.tresorio_renders_details
    for i in range(len(renders)):
        if renders[i - delta].is_target:
            await _delete_render(token, renders[i - delta], i - delta)
            delta += 1


async def _update_user_info(token: str):
    async with Platform() as plt:
        try:
            res_user_info = await plt.req_get_user_info(token, jsonify=True)
            _get_user_info_callback(res_user_info)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            if logout_if_unauthorized(err) is False:
                _get_user_info_error(err)
            elif isinstance(err, ClientResponseError) is False:
                popup(TRADUCTOR['notif']['err_acc_info']
                      [CONFIG_LANG], icon='ERROR')
            return


async def _update_renderpacks_info(token: str):
    async with Platform() as plt:
        try:
            res_renderpacks = await plt.req_get_renderpacks(token, jsonify=True)
            _get_renderpacks_callback(res_renderpacks)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            if logout_if_unauthorized(err) is False:
                _get_renderpacks_error(err)
            elif isinstance(err, ClientResponseError) is False:
                popup(TRADUCTOR['notif']
                      ['err_renderpacks'][CONFIG_LANG], icon='ERROR')
            return


def update_renderings_uptime():
    renders = WM.tresorio_renders_details
    for r in renders:
        if r.status == RenderStatus.RUNNING:
            r.uptime = get_uptime(r.created_at)


async def _refresh_loop(token: str):
    while WM.tresorio_user_props.is_logged is True:
        await _update_user_info(token)
        await _update_list_renderings(token)
        for _ in range(5):
            update_renderings_uptime()
            await asyncio.sleep(1)


async def _connect_to_tresorio(data: Dict[str, str]):
    async with Platform() as plt:
        try:
            BACKEND_LOGGER.debug('Connecting to Tresorio')
            res_connect = await plt.req_connect_to_tresorio(data, jsonify=True)
            _connect_to_tresorio_callback(res_connect)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            _connect_to_tresorio_error(err)
            if isinstance(err, ClientResponseError) is False:
                popup(TRADUCTOR['notif']
                      ['err_connection'][CONFIG_LANG], icon='ERROR')
            return

    await _update_renderpacks_info(res_connect['token'])
    await _refresh_loop(res_connect['token'])


async def _update_list_renderings(token: str):
    renders = WM.tresorio_renders_details
    try:
        async with Platform() as plt:
            res_renders = await plt.req_list_renderings_details(token, jsonify=True)
            nb_new_renders = len(res_renders) - len(renders)
            for _ in range(nb_new_renders):
                _add_renders_details_prop(res_renders[0])
                del res_renders[0]
            for res, render in zip(res_renders, renders):
                _fill_render_details(render, res)
    except (ClientResponseError, Exception) as err:
        BACKEND_LOGGER.error(err)
        if logout_if_unauthorized(err) is False:
            _list_renderings_details_error(err)
        return


async def _update_rendering(render, token: str):
    try:
        async with Platform() as plt:
            BACKEND_LOGGER.debug(f'Updating render {render.id}')
            render_details = await plt.req_get_rendering_details(token, render.id, jsonify=True)
            _fill_render_details(render, render_details)
    except (ClientResponseError, Exception) as err:
        BACKEND_LOGGER.error(err)
        if logout_if_unauthorized(err) is False:
            _list_renderings_details_error(err)
        return


async def _new_render(token: str, create_render: Dict[str, Any], launch_render: Dict[str, Any]):
    """This function creates a new render, packs the textures, uploads the blend
       file, unpacks the textures, and finally launches the rendering."""

    blendfile = bpy.data.filepath
    render_form = bpy.context.scene.tresorio_render_form

    try:
        if render_form.pack_textures is True:
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
        with Lockfile(blendfile, 'a'):
            async with Platform() as plt:
                BACKEND_LOGGER.debug(f'Creating new render')
                render_info = await plt.req_create_render(token, create_render, jsonify=True)
            loop = asyncio.get_running_loop()
            upload = functools.partial(
                force_sync(_upload_blend_file_async), blendfile, render_info)
            res = await loop.run_in_executor(None, upload)
            _upload_blend_file_callback(res)
    except (ClientResponseError, Exception) as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError) and err.status == HTTPStatus.FORBIDDEN:
            popup(TRADUCTOR['notif']['not_enough_credits']
                  [CONFIG_LANG], icon='ERROR')
            return
        elif isinstance(err, ClientResponseError) and err.status == HTTPStatus.SERVICE_UNAVAILABLE:
            popup(TRADUCTOR['notif']['not_enough_servers']
                  [CONFIG_LANG], icon='ERROR')
            return
        elif isinstance(err, ClientResponseError) and err.status == HTTPStatus.CONFLICT:
            popup(TRADUCTOR['notif']['render_name_already_taken']
                  [CONFIG_LANG].format(render_form.rendering_name), icon='ERROR')
            return
        elif logout_if_unauthorized(err) is False:
            popup(TRADUCTOR['desc']['upload_failed']
                  [CONFIG_LANG], icon='ERROR')
            _upload_blend_file_error(err)
        elif not isinstance(err, ClientResponseError):
            popup(TRADUCTOR['notif']
                  ['err_upl_blendfile'][CONFIG_LANG], icon='ERROR')
        return

    finally:
        try:
            if render_form.pack_textures is True:
                bpy.context.scene.tresorio_report_props.unpacking_textures = True
                bpy.ops.file.unpack_all()
                bpy.ops.wm.save_as_mainfile(filepath=blendfile)
        except RuntimeError as err:
            BACKEND_LOGGER.error(err)
            popup(TRADUCTOR['notif']
                  ['cant_unpack_textures'][CONFIG_LANG], icon='ERROR')
        finally:
            bpy.context.scene.tresorio_report_props.unpacking_textures = False

    try:
        async with Platform() as plt:
            BACKEND_LOGGER.debug('Launching render ' + render_info['id'])
            res = await plt.req_launch_render(token, render_info['id'], launch_render, jsonify=True)
            update_list_renderings()
    except (ClientResponseError, Exception) as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError) and err.status == HTTPStatus.SERVICE_UNAVAILABLE:
            popup(TRADUCTOR['notif']['not_enough_servers']
                  [CONFIG_LANG], icon='ERROR')
            return
        elif logout_if_unauthorized(err) is False:
            popup(TRADUCTOR['notif']
                  ['err_launch_render'][CONFIG_LANG], icon='ERROR')
        return
    await _update_list_renderings(token)


async def _stop_render(token: str, render):
    try:
        async with Platform() as plt:
            BACKEND_LOGGER.debug(f'Stopping render {render.id}')
            await plt.req_stop_render(token, render.id, jsonify=True)
    except (ClientResponseError, Exception) as err:
        BACKEND_LOGGER.error(err)
        if logout_if_unauthorized(err) is False:
            popup(TRADUCTOR['notif']
                  ['err_stop_render'][CONFIG_LANG], icon='ERROR')
        return
    await _update_rendering(render, token)


async def _delete_render(token: str, render: str, index: int):
    try:
        async with Platform() as plt:
            render_id = render.id
            BACKEND_LOGGER.debug(f'Deleting render {render_id}')
            await plt.req_delete_render(token, render_id)
            WM.tresorio_renders_details.remove(index)
    except (ClientResponseError, Exception) as err:
        BACKEND_LOGGER.error(err)
        if logout_if_unauthorized(err) is False:
            popup(TRADUCTOR['notif']
                  ['err_delete_render'][CONFIG_LANG], icon='ERROR')
        return


async def _upload_blend_file_async(blendfile: str, render_info: Dict[str, Any]):
    bpy.context.scene.tresorio_report_props.uploading_blend_file = True
    async with AsyncNas(render_info['ip']) as nas:
        BACKEND_LOGGER.debug(f'Uploading for render ' + render_info['id'])
        with PercentReader(blendfile) as file:
            return await nas.upload_content(render_info['id'], file, 'scene.blend', render_info['jwt'])


def _upload_blend_file_sync(blendfile: str, render_info: Dict[str, Any]):
    bpy.context.scene.tresorio_report_props.uploading_blend_file = True
    with SyncNas(render_info['ip']) as nas:
        BACKEND_LOGGER.debug(f'Uploading for render ' + render_info['id'])
        with PercentReader(blendfile) as file:
            return nas.upload_content(render_info['id'], file, 'scene.blend', render_info['jwt'])

# CALLBACKS--------------------------------------------------------------------


def _fill_render_details(render, res: Dict[str, Any], is_new: bool = False):
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
    render.is_target = WM.tresorio_user_settings_props.select_all_renders
    if is_new is True:
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
            new_pack.cost, new_pack.gpu, pack['gpuModel'], new_pack.cpu, pack['cpuModel'], new_pack.ram)
        if i == 0:
            new_pack.is_selected = True
            bpy.context.scene.tresorio_render_form.render_pack = pack['name']
        elif last_selected == pack['name']:
            new_pack.is_selected = True
            bpy.context.scene.tresorio_render_form.render_pack = pack['name']


def _get_user_info_callback(res: ClientResponse) -> None:
    WM.tresorio_user_props.total_credits = res['credits']


def _connect_to_tresorio_callback(res: ClientResponse) -> None:
    bpy.context.scene.tresorio_report_props.login_in = False
    WM.tresorio_user_props.token = res['token']
    WM.tresorio_user_props.is_logged = True


def _upload_blend_file_callback(res: ClientResponse) -> None:
    bpy.context.scene.tresorio_report_props.uploading_blend_file = False


# ERROR HANDLERS---------------------------------------------------------------

def _list_renderings_details_error(err: Exception) -> None:
    bpy.context.scene.tresorio_report_props.are_renders_refreshing = False
    if isinstance(err, ClientResponseError) is False:
        popup(TRADUCTOR['notif']['err_renders'][CONFIG_LANG], icon='ERROR')


def _get_renderpacks_error(err: Exception) -> None:
    bpy.context.scene.tresorio_render_form.render_pack = ''


def _get_user_info_error(err: Exception) -> None:
    WM.tresorio_user_props.is_logged = False
    WM.tresorio_user_props.token = ''


def _upload_blend_file_error(err: Exception) -> None:
    bpy.context.scene.tresorio_report_props.uploading_blend_file = False


def _connect_to_tresorio_error(err: Exception) -> None:
    bpy.context.scene.tresorio_report_props.login_in = False
    if isinstance(err, ClientResponseError) is False:
        return
    if err.status == HTTPStatus.UNAUTHORIZED:
        popup(TRADUCTOR['notif']['invalid_login'][CONFIG_LANG], icon='ERROR')
