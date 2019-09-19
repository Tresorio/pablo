"""Tresorio's only interace with operators"""

import os
import bpy
import asyncio
import aiohttp
from .nas import Nas
from .async_loop import ensure_async_loop, erase_async_loop, kick_async_loop
from src.services.platform import Platform
from src.utils.percent_reader import PercentReader
from src.utils.email import set_email_in_conf, remove_email_from_conf
from dataclasses import dataclass

# TODO a real error handling system
@dataclass
class Render:
    """Render form for Tresorio"""
    name: str
    engine: str
    outputFormat: str
    timeout: int
    renderPack: str
    currentFrame: int
    renderType: str  # 'frame' or 'animation'


@dataclass
class BlendFileDesc:
    """Info required to upload on Nas"""
    name: str
    path: str
    size: int


class TresorioBackend:

    # TO CALL FROM OPS---------------------------------------------------------
    @classmethod
    def new_render(cls, render_type: str):
        """To call on front"""
        bpy.data.window_managers['WinMan'].tresorio_report_props.upload_failed = 0
        props = bpy.data.window_managers['WinMan'].tresorio_render_form
        current_frame = bpy.data.scenes[0].frame_current

        render = Render(
            name=props.rendering_name,
            engine=props.render_engines_list,
            outputFormat=props.output_formats_list,
            timeout=props.timeout,
            renderPack=props.render_farms,
            currentFrame=current_frame,
            renderType=render_type,
        )
        blendfile = BlendFileDesc(
            path=bpy.data.filepath,
            name=os.path.basename(bpy.data.filepath),
            size=os.path.getsize(bpy.data.filepath)
        )

        future = cls._new_render(render, blendfile)
        asyncio.ensure_future(future)
        ensure_async_loop()

    @classmethod
    def connect_to_tresorio(cls, email: str, password: str):
        """Connects the user to Tresorio and fetch its data"""
        bpy.data.window_managers['WinMan'].tresorio_user_props.token = ''

        data = {
            'email': email,
            'password': password
        }

        future = cls._connect_to_tresorio(data)
        asyncio.ensure_future(future)
        ensure_async_loop()

    # ASYNC METHODS------------------------------------------------------------
    @classmethod
    async def _connect_to_tresorio(cls, data: dict):
        async with Platform() as plt:
            bpy.data.window_managers['WinMan'].tresorio_report_props.invalid_logs = 0
            bpy.data.window_managers['WinMan'].tresorio_report_props.login_in = 1
            res = await plt.req_connect_to_tresorio(data, jsonify=True)
            cls._connect_to_tresorio_callback(res)
            token = bpy.data.window_managers['WinMan'].tresorio_user_props.token
            res = await plt.req_get_user_info(token, jsonify=True)
            cls._get_user_info_callback(res)
            res = await plt.req_get_renderpacks(token, jsonify=True)
            # cls._get_renderpacks_callback(res)

    @classmethod
    async def _new_render(cls, render: Render, blendfile: BlendFileDesc):
        res = await cls._upload_blend_file(blendfile)
        cls._upload_blend_file_callback(res)
        # res = await cls._

    @staticmethod
    async def _upload_blend_file(blendfile: BlendFileDesc):
        bpy.data.window_managers['WinMan'].tresorio_report_props.uploading_blend_file = 1
        async with Nas('http://192.168.15.14:7777') as nas:
            with PercentReader(blendfile.path) as file:
                res = await nas.upload_content('tmp_blender', file, blendfile.name)
                return res

    # CALLBACKS----------------------------------------------------------------
    @staticmethod
    def _get_user_info_callback(res):
        if res is None:
            bpy.data.window_managers['WinMan'].tresorio_user_props.is_logged = False
            bpy.data.window_managers['WinMan'].tresorio_user_props.token = ''
        else:
            bpy.data.window_managers['WinMan'].tresorio_report_props.fetched_user_info = 1
            bpy.data.window_managers['WinMan'].tresorio_user_props.total_credits = res['credits']

    @staticmethod
    def _connect_to_tresorio_callback(res: dict):
        bpy.data.window_managers['WinMan'].tresorio_report_props.login_in = 0
        if res is None or 'token' not in res:
            bpy.data.window_managers['WinMan'].tresorio_report_props.invalid_logs = 1
            return

        user_props = bpy.context.window_manager.tresorio_user_props
        if user_props.remember_email is True:
            set_email_in_conf(user_props.email)
        else:
            remove_email_from_conf()

        token = res['token']
        bpy.data.window_managers['WinMan'].tresorio_user_props.token = token
        bpy.context.window_manager.tresorio_user_props.is_logged = True

    @staticmethod
    def _new_render_callback(task: asyncio.Task):
        res = task.result()
        print(f'_new_render_callback res: {res}')

    @staticmethod
    def _upload_blend_file_callback(res: aiohttp.ClientResponse):
        bpy.data.window_managers['WinMan'].tresorio_report_props.uploading_blend_file = 0
        if res is None or res.status < 200 or res.status >= 300:
            bpy.data.window_managers['WinMan'].tresorio_report_props.upload_failed = 1
