"""Tresorio's only interace with operators"""

import os
import bpy
import asyncio
from http import HTTPStatus
from typing import Dict, Any
from src.services.nas import Nas
from src.utils.lockfile import Lockfile
from src.services.platform import Platform
from src.services.loggers import BACKEND_LOGGER
from src.utils.percent_reader import PercentReader
from src.services.async_loop import ensure_async_loop
from aiohttp import ClientResponseError, ClientResponse


def new_render():
    bpy.data.window_managers['WinMan'].tresorio_report_props.connection_error = False
    bpy.data.window_managers['WinMan'].tresorio_report_props.upload_failed = 0
    props = bpy.data.window_managers['WinMan'].tresorio_render_form
    current_frame = bpy.data.scenes[0].frame_current

    render = {
        'name': props.rendering_name,
        'engine': props.render_engines_list,
        'outputFormat': props.output_formats_list,
        'timeout': props.timeout,
        'renderPack': props.render_pack,
        'currentFrame': current_frame,
        'renderType': props.render_types,
    }
    blendfile = {
        'path': bpy.data.filepath,
        'name': os.path.basename(bpy.data.filepath),
        'size': os.path.getsize(bpy.data.filepath),
    }
    token = bpy.data.window_managers['WinMan'].tresorio_user_props.token

    future = _new_render(token, render, blendfile)
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


async def _connect_to_tresorio(data: Dict[str, str]):
    async with Platform() as plt:
        try:
            res_connect = await plt.req_connect_to_tresorio(data, jsonify=True)
            _connect_to_tresorio_callback(res_connect)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            _connect_to_tresorio_error(err)
            if Exception is not ClientResponseError:
                # TODO: traductions
                set_connection_error(err, 'Error while connecting')
            return

        try:
            res_user_info = await plt.req_get_user_info(res_connect['token'], jsonify=True)
            _get_user_info_callback(res_user_info)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            _get_user_info_error(err)
            if Exception is not ClientResponseError:
                set_connection_error(
                    err, 'Error while getting account information')
            return

        ## TODO: ##
        try:
            res_renderpacks = await plt.req_get_renderpacks(res_connect['token'], jsonify=True)
            _get_renderpacks_callback(res_renderpacks)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            _get_renderpacks_error(err)
            if Exception is not ClientResponseError:
                set_connection_error(
                    err, 'Error while getting renderpacks information')
            return


async def _new_render(token: str, render: Dict[str, Any], blendfile: Dict[str, Any]):
    with Lockfile(blendfile['path'], 'a'):
        try:
            res = await _upload_blend_file(blendfile)
            _upload_blend_file_callback(res)
        except (ClientResponseError, Exception) as err:
            BACKEND_LOGGER.error(err)
            _upload_blend_file_error(err)
            if Exception is not ClientResponseError:
                set_connection_error(err, 'Error while uploading blend file')
            return

    # async with Platform() as plt:
    # res = await plt.req_create_render(token, render)


async def _upload_blend_file(blendfile: dict):
    bpy.data.window_managers['WinMan'].tresorio_report_props.uploading_blend_file = 1
    async with Nas('http://192.168.15.14:7777') as nas:
        with PercentReader(blendfile['path']) as file:
            return await nas.upload_content('tmp_blender', file, blendfile['name'])


# CALLBACKS----------------------------------------------------------------
def _get_renderpacks_callback(res: ClientResponse) -> None:
    for i, pack in enumerate(res):
        new_pack = bpy.context.window_manager.tresorio_render_packs.add()
        cost = pack['cost']
        gpu = pack['gpu']
        vcpu = pack['vcpu']
        ram = pack['ram'] / 1024

        new_pack.name = pack['name'].upper()
        new_pack.cost = pack['cost']
        new_pack.description = f'COST: {cost:.2f}/hr | GPU: {gpu} | VCPU: {vcpu} | RAM: {ram} Gio'
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


# ERROR HANDLERS-----------------------------------------------------------
def _get_renderpacks_error(err: Exception) -> None:
    pass


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
