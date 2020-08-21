"""Tresorio's only interace with operators"""

from http import HTTPStatus
from datetime import datetime
from typing import Dict, Any, List
from collections.abc import Coroutine
from queue import Queue
import boto3
from botocore.config import Config
import io
import os
import shutil
import asyncio
import functools
import tempfile
import sys

import bpy
import time
import pathlib
from src.ui.popup import popup, alert, notif
from src.operators.logout import logout
from src.services.tresorio_platform import Platform, backend_url
from src.utils.decompress import decompress_rendering_results, get_extract_path
from src.utils.force_sync import force_sync
from src.services.nas import AsyncNas, SyncNas
from src.services.loggers import BACKEND_LOGGER
from src.config.api import API_CONFIG, MODE
from src.utils.percent_reader import PercentReader
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.operators.async_loop import ensure_async_loop
from src.config.enums import RenderStatus, RenderTypes
from src.properties.render_form import get_render_type
from src.properties.renders import TresorioRendersDetailsProps
from bundle_modules.aiohttp import ClientResponseError, ClientResponse
from src.utils.open_image import open_image

import src.operators.upload_modal

# pylint: disable=assignment-from-no-return,assignment-from-none,unexpected-keyword-arg
UPDATE_QUEUE = Queue()


def logout_if_unauthorized(err: ClientResponseError) -> None:
    """Log the user out if its cookie became invalid

    Arg:
        err: The error that appeared doing a request to the backend of Tresorio
    """
    if err.status == HTTPStatus.UNAUTHORIZED:
        logout(bpy.context)
        popup(TRADUCTOR['notif']['expired_session'][CONFIG_LANG], icon='ERROR')


def get_farms(rendering_mode: str, number_of_frames: int) -> None:
    cookie = bpy.context.window_manager.tresorio_user_props.cookie

    future = _get_farms(cookie, rendering_mode, number_of_frames)
    asyncio.ensure_future(future)

def new_upload(blend_path: str, target_path: str, project_name: str) -> None:
    """Upload a new blend file"""

    cookie = bpy.context.window_manager.tresorio_user_props.cookie

    future = _chunked_upload(cookie, blend_path, target_path, project_name)
    asyncio.ensure_future(future)


def resume_render(render, farm_index) -> None:
    """Resume an already existing render"""

    cookie = bpy.context.window_manager.tresorio_user_props.cookie

    future = _resume_render(cookie, render, farm_index)
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

    project_name = bpy.path.clean_name(bpy.context.scene.tresorio_render_form.project_name)

    launch_render = {
        'name': props.rendering_name,
        'engine': props.render_engines_list,
        'outputFormat': props.output_formats_list,
        'renderingMode': bpy.context.window_manager.tresorio_user_props.rendering_mode,
        'farmIndex': bpy.context.window_manager.tresorio_farm_props_index,
        'autoTileSize': props.auto_tile_size,
        'optix': props.use_optix,
        'startingFrame': starting_frame,
        'endingFrame': ending_frame,
        'projectName': project_name,
        'sceneName': os.path.basename(bpy.data.filepath)
    }
    cookie = bpy.context.window_manager.tresorio_user_props.cookie

    future = _new_render(cookie, launch_render)
    asyncio.ensure_future(future)


def connect_to_tresorio(email: str,
                        password: str
                        ) -> None:
    """Connects the user to Tresorio and fetch required data"""
    credentials = {
        'email': email,
        'password': password,
        'extended': False,
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
    cookie = bpy.context.window_manager.tresorio_user_props.cookie
    future = _delete_render(cookie, render_id)
    asyncio.ensure_future(future)


def stop_render(render: TresorioRendersDetailsProps) -> None:
    """Stop a render

    Arg:
        render: The render to stop
    """
    cookie = bpy.context.window_manager.tresorio_user_props.cookie
    future = _stop_render(cookie, render)
    asyncio.ensure_future(future)


def download_render_results(render_id: str,
                            render_result_path: str
                            ) -> None:
    """Download the results of a render

    Args:
        render_id: The unique id of the render to target
        render_result_path: the filepath where to write the downloaded results
    """
    cookie = bpy.context.window_manager.tresorio_user_props.cookie
    future = _download_folder_from_S3(cookie, render_id, render_result_path)
    asyncio.ensure_future(future)


def update_list_renderings():
    """Update all the renderings"""
    cookie = bpy.context.window_manager.tresorio_user_props.cookie
    future = _update_list_renderings(cookie)
    asyncio.ensure_future(future)


def delete_all_renders():
    """Delete all the renders"""
    cookie = bpy.context.window_manager.tresorio_user_props.cookie
    future = _delete_all_renders(cookie)
    asyncio.ensure_future(future)


def _download_folder_from_S3(render_result_path: str,
               render: TresorioRendersDetailsProps,
               open_on_download: bool = False):

    user=bpy.context.window_manager.tresorio_user_props

    ### Hardcoded configuration needed to communicate with MinIO
    config = Config(
        s3={
          "addressing_style":"virtual"
        },
        signature_version='s3v4',
    )

    s3_resource = boto3.resource(
        's3',
        aws_access_key_id=user.access_key,
        aws_secret_access_key=user.secret_key,
        endpoint_url=API_CONFIG[MODE]['storage'],
        config=config,
    )
    bucket = s3_resource.Bucket(name=f'{user.id}-renderings')

    ### WILL BE AVAILABLE IN RENDER DETAILS
    remoteDir = render.project_id

    ### Add suffix after target directory if it does already exist
    os.makedirs(render_result_path, exist_ok=True)
    counter = 1
    subdir = render.name
    target_dir = os.path.join(render_result_path, subdir)
    while os.path.exists(target_dir):
        subdir = render.name+"("+str(counter)+")"
        target_dir = os.path.join(render_result_path, subdir)
        counter += 1

    try:
        for object in bucket.objects.filter(Prefix = remoteDir):
            print("Downloading "+object.key+" (size: "+str(object.size)+")...")
            filename=os.path.join(target_dir, object.key)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb+') as file:
                bucket.download_fileobj(object.key, file, Callback=callback)

        if open_on_download:
            # Open the outputs directory if there is no error, else base directory
            if render.status != RenderStatus.ERROR:
                open_path = os.path.join(extract_path, 'outputs', 'frames')
                if not os.path.isdir(open_path):
                    open_path = ""
            else:
                open_path = ""
            abs_open_path = os.path.join(extract_path, open_path)
            open_image(abs_open_path)

        UPDATE_QUEUE.put(('finished_download', render.id))

    except Exception as err:
        BACKEND_LOGGER.error(err)
        UPDATE_QUEUE.put(('finished_download', render.id))
        raise

# ASYNC CORE-------------------------------------------------------------------

async def _download_render_results(cookie: str,
                                   render: TresorioRendersDetailsProps,
                                   render_result_path: str
                                   ) -> Coroutine:
    try:
        user_settings = bpy.context.window_manager.tresorio_user_settings_props
        loop = asyncio.get_running_loop()
        open_on_dl = user_settings.open_image_on_download
        download = functools.partial(
            _download_folder_from_S3folder_from_S3,
            render_result_path,
            render,
            open_on_dl,
        )
        render.downloading = True
        await loop.run_in_executor(None, download)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        UPDATE_QUEUE.put(('finished_download', render_details['id']))
        alert(TRADUCTOR['notif']['err_download_folder_from_S3results']
              [CONFIG_LANG])


async def _update_user_info(cookie: str,
                            silence_errors: bool = False
                            ) -> Coroutine:
    async with Platform() as plt:
        try:
            res_user_info = await plt.req_get_user_info(cookie, jsonify=True)
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


async def _refresh_loop(cookie: str) -> Coroutine:
    comms = {
        'upload_percent': update_upload_percent,
        'finished_upload': update_finished_upload,
        'finished_download': update_finished_download,
    }
    is_logged = bpy.context.window_manager.tresorio_user_props.is_logged
    while is_logged:
        await _update_user_info(cookie, silence_errors=True)
        await _update_list_renderings(cookie, silence_errors=True)
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
            res = await plt.req_connect_to_tresorio(data, jsonify=False)
            session_cookie = res.cookies['connect.sid'].value
            bpy.context.window_manager.tresorio_user_props.cookie = session_cookie
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
            await _refresh_loop(session_cookie)


async def _update_list_renderings(cookie: str,
                                  silence_errors: bool = False
                                  ) -> Coroutine:
    try:
        async with Platform() as plt:
            res_renders = await plt.req_list_renderings_details(cookie, jsonify=True)
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
                            cookie: str
                            ) -> Coroutine:
    try:
        async with Platform() as plt:
            BACKEND_LOGGER.debug(f'Updating render {render.id}')
            render_details = await plt.req_get_rendering_details(cookie, render.id, jsonify=True)
            _fill_render_details(render, render_details)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup(TRADUCTOR['notif']['err_render'][CONFIG_LANG], icon='ERROR')
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)

def _on_upload_start(target_path: str):
    print('[UPL START]')
    bpy.context.scene.tresorio_render_form.upload_percent = 0.0
    bpy.context.window_manager.tresorio_report_props.uploading_blend_file = True

def _on_upload_progress(filename: str, progress: float):
    bpy.context.scene.tresorio_render_form.file_uploading = filename
    bpy.context.scene.tresorio_render_form.upload_percent = progress

def _on_upload_end(target_path: str, success: bool):
    print('[UPL END]')
    bpy.context.scene.tresorio_render_form.upload_percent = 0.0
    bpy.context.window_manager.tresorio_report_props.uploading_blend_file = False
    bpy.context.scene.tresorio_render_form.file_uploading = ''
    bpy.context.window_manager.tresorio_report_props.uploading = False

def _on_upload_error(filename: str, error: str):
    print('[UPL ERROR]')
    alert(TRADUCTOR['notif']['err_upl'][CONFIG_LANG].format(filename, error))

def _on_pack_start(blend_path: str, target_path: str):
    print('[PACK START]')
    bpy.context.window_manager.tresorio_report_props.packing_textures = True
    bpy.context.scene.tresorio_render_form.pack_percent = 0.0

def _on_pack_progress(progress: float):
    bpy.context.scene.tresorio_render_form.pack_percent = progress

def _on_pack_error(blend_path: str, target_path: str, error: str):
    print('[PACK ERROR]')
    alert(TRADUCTOR['notif']['cant_pack_textures'][CONFIG_LANG], subtitle=error)

def _on_missing_file(blend_path: str, target_path: str, file: str):
    print('[MISSING FILE]')
    notif(TRADUCTOR['notif']['missing_file'][CONFIG_LANG].format(file))

def _on_pack_end(blend_path: str, target_path: str, success: bool):
    print('[PACK END]')
    bpy.context.scene.tresorio_render_form.pack_percent = 0.0
    bpy.context.window_manager.tresorio_report_props.packing_textures = False
    bpy.context.window_manager.tresorio_report_props.uploading_blend_file = True

def _on_project_creation_error(project_name: str, error: str):
    print('[PROJECT CREATION ERROR]')
    alert(TRADUCTOR['notif']['error_project'][CONFIG_LANG].format(project_name), subtitle=error)

def _on_end(exit_code: int):
    print('[END]')
    print('Exited with ', exit_code)
    bpy.context.window_manager.tresorio_report_props.uploading = False
    bpy.context.scene.tresorio_render_form.upload_percent = 0.0
    bpy.context.window_manager.tresorio_report_props.uploading_blend_file = False
    bpy.context.scene.tresorio_render_form.pack_percent = 0.0
    bpy.context.window_manager.tresorio_report_props.packing_textures = False
    bpy.context.scene.tresorio_render_form.file_uploading = ''
    if exit_code == 0:
        notif(TRADUCTOR['notif']['exported'][CONFIG_LANG])

def _on_unknown_error(error: str):
    print('[UNKNOWN ERROR]')
    alert(TRADUCTOR['notif']['unknown_error_upl'][CONFIG_LANG], subtitle=error)

async def _chunked_upload(cookie: str, blend_path: str, target_path: str, project_name: str) -> Coroutine:
    """This function upload a new .blend file"""

    render_form = bpy.context.scene.tresorio_render_form
    bpy.context.window_manager.tresorio_report_props.uploading = True

    try:
        src.operators.upload_modal.end_callback = _on_end
        src.operators.upload_modal.error_callback = _on_unknown_error

        src.operators.upload_modal.pack_start_callback = _on_pack_start
        src.operators.upload_modal.pack_progress_callback = _on_pack_progress
        src.operators.upload_modal.pack_end_callback = _on_pack_end
        src.operators.upload_modal.pack_error_callback = _on_pack_error
        src.operators.upload_modal.missing_file_callback = _on_missing_file
        src.operators.upload_modal.project_creation_error_callback = _on_project_creation_error

        src.operators.upload_modal.upload_start_callback = _on_upload_start
        src.operators.upload_modal.upload_progress_callback = _on_upload_progress
        src.operators.upload_modal.upload_end_callback = _on_upload_end
        src.operators.upload_modal.upload_error_callback = _on_upload_error


        bpy.ops.tresorio.upload_modal(
            blend_path = blend_path,
            target_path = target_path,
            project_name = project_name,
            url = backend_url,
            jwt = cookie
        )


    except Exception as err:
        bpy.context.window_manager.tresorio_report_props.uploading = False
        bpy.context.scene.tresorio_render_form.upload_percent = 0.0
        bpy.context.window_manager.tresorio_report_props.uploading_blend_file = False
        bpy.context.scene.tresorio_render_form.pack_percent = 0.0
        bpy.context.window_manager.tresorio_report_props.packing_textures = False
        bpy.context.scene.tresorio_render_form.file_uploading = ''
        BACKEND_LOGGER.error(err)
        popup_msg = TRADUCTOR['notif']['err_upl_blendfile'][CONFIG_LANG]
        alert(popup_msg)


async def _new_upload(cookie: str, path: str, project_name: str) -> Coroutine:
    """This function upload a new .blend file"""

    render_form = bpy.context.scene.tresorio_render_form
    render_info = None

    print("Uploading", path)
    bpy.context.window_manager.tresorio_report_props.uploading_blend_file = True

    try:
        async with Platform() as plt:
            render_info = await plt.req_create_render(cookie, os.path.getsize(path), project_name, jsonify=True)
            bpy.context.scene.tresorio_render_form.project_id = render_info['id']
        try:
            await _update_list_renderings(cookie)
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
    cookie: str,
    rendering_mode: str,
    number_of_frames: int
) -> Coroutine:
    try:
        async with Platform() as plt:
            farms = await plt.req_get_farms(cookie, {
                'renderingMode': rendering_mode,
                'numberOfFrames': number_of_frames
            }, jsonify=True)
            if len(farms) == 0:
                bpy.context.window_manager.tresorio_user_props.is_launching_rendering = False
                BACKEND_LOGGER.error("Empty response from server while getting farms")
                alert(TRADUCTOR['notif']['something_went_wrong'][CONFIG_LANG])
                return
            for farm in farms:
                print(farm)
                item = bpy.context.window_manager.tresorio_farm_props.add()
                item.cost = farm["costPerHour"]
                item.gpu = farm["totalResources"]["gpus"]["SAAS"]
                item.cpu = farm["totalResources"]["cpus"]
                # Ram is converted into MB
                item.ram = farm["totalResources"]["ram"] / (1000 * 1000)
                item.is_available = farm["isAvailable"]
                item.units_per_farmer = farm["singleFarmerResources"]["units"]
                item.number_of_farmers = farm["farmersCount"]
    except Exception as err:
        bpy.context.window_manager.tresorio_user_props.is_launching_rendering = False
        BACKEND_LOGGER.error(err)
        alert(TRADUCTOR['notif']['something_went_wrong'][CONFIG_LANG])


async def _resume_render(cookie: str,
                        render,
                        farm_index: int
                        ) -> Coroutine:
    """Resume rendering"""

    try:
        async with Platform() as plt:
            await plt.req_resume_render(cookie, render.id, farm_index, jsonify=True)
            await _update_list_renderings(cookie)
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


async def _new_render(cookie: str,
                      launch_render: Dict[str, Any]
                      ) -> Coroutine:
    """This function creates a new render and launches it."""

    render_form = bpy.context.scene.tresorio_render_form

    try:
        async with Platform() as plt:
            launch_render['projectId'] = render_form.project_id
            await plt.req_launch_render(cookie, launch_render, jsonify=True)
            await _update_list_renderings(cookie)
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

async def _stop_render(cookie: str,
                       render: TresorioRendersDetailsProps
                       ) -> Coroutine:
    try:
        async with Platform() as plt:
            BACKEND_LOGGER.debug(f'Stopping render {render.id}')
            await plt.req_stop_render(cookie, render.id, jsonify=True)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
        alert(TRADUCTOR['notif']['err_stop_render'][CONFIG_LANG])
    else:
        await _update_rendering(render, cookie)


async def _delete_render(cookie: str,
                         render_id: str,
                         ) -> Coroutine:
    try:
        async with Platform() as plt:
            renders = await plt.req_delete_render(cookie, render_id, jsonify=True)
            update_ui_renderings(renders, is_new=True)
    except Exception as err:
        BACKEND_LOGGER.error(err)
        if isinstance(err, ClientResponseError):
            logout_if_unauthorized(err)
        alert(TRADUCTOR['notif']['err_delete_render'][CONFIG_LANG])


async def _delete_all_renders(cookie: str) -> Coroutine:
    try:
        bpy.context.window_manager.tresorio_report_props.deleting_all_renders = True
        async with Platform() as plt:
            renders = await plt.req_list_renderings_details(cookie, jsonify=True)
            for render in renders:
                await _delete_render(cookie, render['id'])
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
    render.project_id = res['projectId']
    render.name = res['name']
    render.cpu = res['vcpu']
    render.gpu = res['gpu']
    render.ram = res['ram']
    render.cost = res['costPerHour']
    render.total_cost = res['cost']
    render.engine = res['engine']
    render.type = res['renderType']
    render.output_format = res['outputFormat']
    render.status = res['status']
    render.total_frames = res['numberOfFrames']
    render.rendered_frames = res['finishedFrames']
    render.progress = res['progress']
    render.number_of_fragments = res['fragmentCount']
    render.uptime = res['uptime']
    render.mode = res['mode']

    render.is_downloadable = res['isDownloadable']
    render.is_stoppable = res['isStoppable']
    render.is_resumable = res['isResumable']
    render.is_restartable = res['isRestartable']

def _add_renders_details_prop(res: Dict[str, Any]) -> None:
    render = bpy.context.window_manager.tresorio_renders_details.add()
    _fill_render_details(render, res, is_new=True)


def _get_user_info_callback(res: ClientResponse) -> None:
    bpy.context.window_manager.tresorio_user_props.total_credits = res['credits']
    bpy.context.window_manager.tresorio_user_props.access_key = res['accessKey']
    bpy.context.window_manager.tresorio_user_props.secret_key = res['secretKey']
    bpy.context.window_manager.tresorio_user_props.id = res['id']
