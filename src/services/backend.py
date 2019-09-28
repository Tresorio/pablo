"""Tresorio's only interace with operators"""

import os
import bpy
import asyncio
from http import HTTPStatus
from typing import Dict, Any
from src.services.nas import Nas
from src.operators.logout import logout
from src.utils.lockfile import Lockfile
from src.services.platform import Platform
from src.services.loggers import BACKEND_LOGGER
from src.utils.percent_reader import PercentReader
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.async_loop import ensure_async_loop
from src.config.debug import NAS_DEBUG, PLATFORM_DEBUG
from aiohttp import ClientResponseError, ClientResponse
from src.properties.renders import update_renders_details_prop


def logout_if_unauthorized(err: Exception):
    if type(err) is ClientResponseError and err.status == HTTPStatus.UNAUTHORIZED:
        logout()
        set_connection_error(
            err, TRADUCTOR['notif']['expired_session'][CONFIG_LANG])
        return True
    return False


def new_render():
    bpy.data.window_managers['WinMan'].tresorio_report_props.connection_error = False
    bpy.data.window_managers['WinMan'].tresorio_report_props.upload_failed = 0
    props = bpy.data.window_managers['WinMan'].tresorio_render_form

    create_render = {
        'name': props.rendering_name,
        'engine': props.render_engines_list,
        'outputFormat': props.output_formats_list,
        'timeout': props.timeout,
        'farm': props.render_pack,
        'renderType': props.render_types,
        'size': os.path.getsize(bpy.data.filepath),
    }
    launch_render = {
        'currentFrame': bpy.data.scenes[0].frame_current,
        'startingFrame': bpy.data.scenes[0].frame_start,
        'endingFrame': bpy.data.scenes[0].frame_end,
    }
    token = bpy.data.window_managers['WinMan'].tresorio_user_props.token

    future = _new_render(token, create_render, launch_render)
    asyncio.ensure_future(future)
    ensure_async_loop()


def connect_to_tresorio(email: str, password: str):
    """Connects the user to Tresorio and fetch required data"""
    bpy.data.window_managers['WinMan'].tresorio_report_props.connection_error = False
    bpy.data.window_managers['WinMan'].tresorio_user_props.token = ''
    bpy.data.window_managers['WinMan'].tresorio_report_props.invalid_logs = 0
    bpy.data.window_managers['WinMan'].tresorio_report_props.login_in = 1

    credentials = {
        'email': email,
        'password': password
    }

    future = _connect_to_tresorio(credentials)
    asyncio.ensure_future(future)
    ensure_async_loop()


def set_connection_error(err: Exception, msg: str):
    bpy.data.window_managers['WinMan'].tresorio_report_props.connection_error = True
    bpy.data.window_managers['WinMan'].tresorio_report_props.connection_error_msg = msg

# ASYNC CORE-------------------------------------------------------------------


async def _connect_to_tresorio(data: Dict[str, str]):
    # Get token
    async with Platform(debug=PLATFORM_DEBUG) as plt:
        try:
            res_connect = await plt.req_connect_to_tresorio(data, jsonify=True)
            _connect_to_tresorio_callback(res_connect)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            _connect_to_tresorio_error(err)
            if type(err) is not ClientResponseError:
                set_connection_error(
                    err, TRADUCTOR['notif']['err_connection'][CONFIG_LANG])
            return

    # Get user specific information
        try:
            res_user_info = await plt.req_get_user_info(res_connect['token'], jsonify=True)
            _get_user_info_callback(res_user_info)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            if logout_if_unauthorized(err) is False:
                _get_user_info_error(err)
            if type(err) is not ClientResponseError:
                set_connection_error(
                    err, TRADUCTOR['notif']['err_acc_info'][CONFIG_LANG])
            return

    # Get render packs information
        try:
            res_renderpacks = await plt.req_get_renderpacks(res_connect['token'], jsonify=True)
            _get_renderpacks_callback(res_renderpacks)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            if logout_if_unauthorized(err) is False:
                _get_renderpacks_error(err)
            if type(err) is not ClientResponseError:
                set_connection_error(
                    err, TRADUCTOR['notif']['err_renderpacks'][CONFIG_LANG])
            return


async def _new_render(token: str, create_render: Dict[str, Any], launch_render: Dict[str, Any]):
    blendfile = bpy.data.filepath
    # Create render and upload blend file
    with Lockfile(blendfile, 'a'):
        try:
            async with Platform(debug=PLATFORM_DEBUG) as plt:
                render_info = await plt.req_create_render(token, create_render, jsonify=True)
            res = await _upload_blend_file(blendfile, render_info)
            _upload_blend_file_callback(res)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            if logout_if_unauthorized(err) is False:
                _upload_blend_file_error(err)
            if type(err) is not ClientResponseError:
                set_connection_error(
                    err, TRADUCTOR['notif']['err_upl_blendfile'][CONFIG_LANG])
            return

    # Launch rendering
    try:
        async with Platform(debug=PLATFORM_DEBUG) as plt:
            res = await plt.req_launch_render(token, render_info['id'], launch_render, jsonify=True)
            _new_render_callback(res)
    except (ClientResponseError, Exception) as err:
        BACKEND_LOGGER.error(err)
        if logout_if_unauthorized(err) is False:
            set_connection_error(
                err, 'Error while creating the new render (TODO Traduction)')
        return


async def _upload_blend_file(blendfile: str, render_info: Dict[str, Any]):
    bpy.data.window_managers['WinMan'].tresorio_report_props.uploading_blend_file = 1
    async with Nas(render_info['ip'], debug=NAS_DEBUG) as nas:
        with PercentReader(blendfile) as file:
            return await nas.upload_content(render_info['id'], file, 'scene.blend', render_info['jwt'])


# CALLBACKS--------------------------------------------------------------------
def _new_render_callback(res: Dict[str, Any]):
    update_renders_details_prop(res)


def _get_renderpacks_callback(res: ClientResponse) -> None:
    bpy.context.window_manager.property_unset('tresorio_render_packs')
    for i, pack in enumerate(res):
        new_pack = bpy.context.window_manager.tresorio_render_packs.add()
        cost = pack['cost']
        gpu = pack['gpu']
        vcpu = pack['vcpu']
        ram = pack['ram'] / 1024  # Mib to Gio

        new_pack.name = pack['name']
        new_pack.cost = pack['cost']
        new_pack.description = f'{cost} credits per hour|{gpu} gpu and {vcpu} vcpu|{ram} Gio of ram'
        if i == 0:
            new_pack.is_selected = True


def _get_user_info_callback(res: ClientResponse) -> None:
    bpy.data.window_managers['WinMan'].tresorio_user_props.total_credits = res['credits']


def _connect_to_tresorio_callback(res: ClientResponse) -> None:
    bpy.data.window_managers['WinMan'].tresorio_report_props.login_in = False
    bpy.data.window_managers['WinMan'].tresorio_user_props.token = res['token']
    bpy.context.window_manager.tresorio_user_props.is_logged = True


def _upload_blend_file_callback(res: ClientResponse) -> None:
    bpy.data.window_managers['WinMan'].tresorio_report_props.uploading_blend_file = False


# ERROR HANDLERS---------------------------------------------------------------
def _get_renderpacks_error(err: Exception) -> None:
    bpy.data.window_managers['WinMan'].tresorio_render_form.render_pack = ''


def _get_user_info_error(err: Exception) -> None:
    bpy.data.window_managers['WinMan'].tresorio_user_props.is_logged = False
    bpy.data.window_managers['WinMan'].tresorio_user_props.token = ''


def _upload_blend_file_error(err: Exception) -> None:
    bpy.data.window_managers['WinMan'].tresorio_report_props.uploading_blend_file = False
    bpy.data.window_managers['WinMan'].tresorio_report_props.upload_failed = True


def _connect_to_tresorio_error(err: Exception) -> None:
    bpy.data.window_managers['WinMan'].tresorio_report_props.login_in = False
    if type(err) is not ClientResponseError:
        return
    if err.status == HTTPStatus.UNAUTHORIZED:
        bpy.data.window_managers['WinMan'].tresorio_report_props.invalid_logs = True
