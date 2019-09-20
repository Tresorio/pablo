"""Tresorio's only interace with operators"""

import os
import bpy
import asyncio
import aiohttp
from typing import Union
from src.services.nas import Nas
from src.utils.lockfile import Lockfile
from src.services.platform import Platform
from src.utils.percent_reader import PercentReader
from src.services.async_loop import ensure_async_loop


class TresorioBackend:
    """Regroups the methods to use on the front interface"""

    # TO CALL WITH OPS---------------------------------------------------------
    @classmethod
    def new_render(cls):
        """To call on front"""
        bpy.data.window_managers['WinMan'].tresorio_report_props.upload_failed = 0
        props = bpy.data.window_managers['WinMan'].tresorio_render_form
        current_frame = bpy.data.scenes[0].frame_current

        # TODO format validator on args
        render = {
            'name': props.rendering_name,
            'engine': props.render_engines_list,
            'outputFormat': props.output_formats_list,
            'timeout': props.timeout,
            'renderPack': props.render_farms,
            'currentFrame': current_frame,
            'renderType': props.render_types,
        }
        blendfile = {
            'path': bpy.data.filepath,
            'name': os.path.basename(bpy.data.filepath),
            'size': os.path.getsize(bpy.data.filepath),
        }
        token = bpy.data.window_managers['WinMan'].tresorio_user_props.token

        future = cls._new_render(token, render, blendfile)
        asyncio.ensure_future(future)
        ensure_async_loop()

    @classmethod
    def connect_to_tresorio(cls, email: str, password: str):
        """Connects the user to Tresorio and fetch its data"""
        bpy.data.window_managers['WinMan'].tresorio_user_props.token = ''
        bpy.data.window_managers['WinMan'].tresorio_report_props.invalid_logs = 0
        bpy.data.window_managers['WinMan'].tresorio_report_props.login_in = 1

        # TODO format validator on args
        credentials = {
            'email': email,
            'password': password
        }

        future = cls._connect_to_tresorio(credentials)
        asyncio.ensure_future(future)
        ensure_async_loop()

    # ASYNC METHODS------------------------------------------------------------
    @classmethod
    async def _connect_to_tresorio(cls, data: dict):
        async with Platform(debug=True) as plt:
            res_connect = await plt.req_connect_to_tresorio(data, jsonify=True)
            cls._connect_to_tresorio_callback(res_connect)
            res_user_info = await plt.req_get_user_info(res_connect['token'], jsonify=True)
            cls._get_user_info_callback(res_user_info)
            # res_renderpacks = await plt.req_get_renderpacks(res_connect['token'], jsonify=True)
            # cls._get_renderpacks_callback(res_renderpacks)

    @classmethod
    async def _new_render(cls, token: str, render: dict, blendfile: dict):
        with Lockfile(blendfile['path'], 'a'):
            try:
                res = await cls._upload_blend_file(blendfile)
                cls._upload_blend_file_callback(res)
            except aiohttp.ClientResponseError as err:
                cls._upload_blend_file_callback(err)

        async with Platform() as plt:
            res = await plt.req_create_render(token, render)

    @staticmethod
    async def _upload_blend_file(blendfile: dict):
        bpy.data.window_managers['WinMan'].tresorio_report_props.uploading_blend_file = 1
        async with Nas('http://192.168.15.14:7777') as nas:
            with PercentReader(blendfile['path']) as file:
                return await nas.upload_content('tmp_blender', file, blendfile['name'])

    # CALLBACKS----------------------------------------------------------------
    @staticmethod
    def _get_user_info_callback(res: dict):
        if 'credits' not in res:
            bpy.data.window_managers['WinMan'].tresorio_user_props.is_logged = False
            bpy.data.window_managers['WinMan'].tresorio_user_props.token = ''
        else:
            bpy.data.window_managers['WinMan'].tresorio_user_props.total_credits = res['credits']

    @staticmethod
    def _connect_to_tresorio_callback(res: dict):
        bpy.data.window_managers['WinMan'].tresorio_report_props.login_in = 0

        if 'token' not in res:
            bpy.data.window_managers['WinMan'].tresorio_report_props.invalid_logs = 1
        else:
            bpy.data.window_managers['WinMan'].tresorio_user_props.token = res['token']
            bpy.context.window_manager.tresorio_user_props.is_logged = True

    @staticmethod
    def _upload_blend_file_callback(res: Union[aiohttp.ClientResponse, aiohttp.ClientResponseError], error: bool = False):
        bpy.data.window_managers['WinMan'].tresorio_report_props.uploading_blend_file = 0
        if error is True:
            bpy.data.window_managers['WinMan'].tresorio_report_props.upload_failed = True
    # ERROR HANDLERS-----------------------------------------------------------
