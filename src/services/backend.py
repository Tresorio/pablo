"""Tresorio's only interace with operators"""

import os
import bpy
import asyncio
import aiohttp
from .nas import Nas
from .async_loop import ensure_async_loop
from src.services.platform import Platform
from src.utils.percent_reader import PercentReader
from src.utils.email import set_email_in_conf, remove_email_from_conf
from dataclasses import dataclass


@dataclass
class Render:
    """Render form for Tresorio"""
    name: str
    engine: str
    output_format: str
    timeout: int
    render_pack: str
    current_frame: int
    render_type: str  # 'frame' or 'animation'


class TresorioBackend:

    @staticmethod
    async def get_upload_nas(self):
        pass

    @staticmethod
    def _upload_blend_file_callback(task: asyncio.Task):
        res = task.result()
        bpy.data.window_managers['WinMan'].tresorio_report_props.uploading_blend_file = 0
        if res is None or res.status < 200 or res.status >= 300:
            bpy.data.window_managers['WinMan'].tresorio_report_props.upload_failed = 1

    @staticmethod
    async def _upload_blend_file():
        # TODO: query Gandalf to get Nassim token and uuid
        # nas_task = asyncio.ensure_future(self.get_upload_nas())
        # nas_task.add_done_callback(any_sync_func_ptr)
        # nas_spec = async_loop.ensure_async_loop()
        filepath = bpy.data.filepath
        blendfile_name = os.path.basename(filepath)
        bpy.data.window_managers['WinMan'].tresorio_report_props.uploading_blend_file = 1
        async with Nas('http://192.168.15.14:7777') as nas:
            with PercentReader(filepath) as file:
                res = await nas.upload_content('tmp_blender', file, blendfile_name)
                return res

    @staticmethod
    def _new_render_callback(task: asyncio.Task):
        res = task.result()
        print(f'_new_render_callback res: {res}')

    @classmethod
    async def _new_render(cls, render: Render):
        upl_res = await cls._upload_blend_file()
        return upl_res

    @classmethod
    def new_render(cls, render_type: str):
        """To call on front"""
        bpy.data.window_managers['WinMan'].tresorio_report_props.upload_failed = 0

        props = bpy.data.window_managers['WinMan'].tresorio_render_form
        current_frame = bpy.data.scenes[0].frame_current
        render = Render(
            name=props.rendering_name,
            engine=props.render_engines_list,
            output_format=props.output_formats_list,
            timeout=props.timeout,
            render_pack=props.render_farms,
            current_frame=current_frame,
            render_type=render_type,
        )
        future = cls._new_render(render)
        task = asyncio.ensure_future(future)
        task.add_done_callback(cls._upload_blend_file_callback)
        ensure_async_loop()

    @classmethod
    def _connect_to_tresorio_callback(cls, task: asyncio.Task):
        res = task.result()
        user_props = bpy.context.window_manager.tresorio_user_props

        bpy.data.window_managers['WinMan'].tresorio_report_props.login_in = 0
        if res is None or 'token' not in res:
            bpy.data.window_managers['WinMan'].tresorio_report_props.invalid_logs = 1
            return

        if user_props.remember_email is True:
            set_email_in_conf(user_props.email)
        else:
            remove_email_from_conf()

        token = res['token']
        bpy.data.window_managers['WinMan'].tresorio_user_props.token = token
        bpy.context.window_manager.tresorio_user_props.is_logged = True

    @staticmethod
    async def _connect_to_tresorio(data: dict):
        async with Platform() as plt:
            res = await plt.req_connect_to_tresorio(data, jsonify=True)
            return res

    @classmethod
    def connect_to_tresorio(cls, email: str, password: str):
        """To call on front"""
        bpy.data.window_managers['WinMan'].tresorio_user_props.token = ''

        data = {
            'email': email,
            'password': password
        }

        future = cls._connect_to_tresorio(data)
        task = asyncio.ensure_future(future)
        task.add_done_callback(cls._connect_to_tresorio_callback)
        ensure_async_loop()

    @staticmethod
    def _fill_user_info_callback(task: asyncio.Task):
        res = task.result()
        if res is None:
            # deconnect and print error
            return
        bpy.data.window_managers['WinMan'].tresorio_report_props.fetched_user_info = 1
        bpy.data.window_managers['WinMan'].tresorio_user_props.credits = res['credits']

    @staticmethod
    async def _get_user_info():
        jwt = bpy.data.window_managers['WinMan'].tresorio_user_props.token
        async with Platform() as plt:
            future = await plt.req_get_user_info(jwt, jsonify=True)
            return future

    @classmethod
    def fill_user_info(cls):
        future = cls._get_user_info()
        task = asyncio.ensure_future(future)
        task.add_done_callback(cls._fill_user_info_callback)
        ensure_async_loop()
