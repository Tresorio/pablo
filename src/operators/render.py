import os
import bpy
import asyncio
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.services.backend import Renderer, Render
import src.services.async_loop as async_loop


class TresorioRenderFrameOperator(bpy.types.Operator):
    bl_idname = 'tresorio.render_frame'
    bl_label = 'Render frame'

    render_type: bpy.props.StringProperty(options={'SKIP_SAVE', 'HIDDEN'})

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['tresorio_render_frame'][CONFIG_LANG]

    def execute(self, context):
        user_props = context.window_manager.tresorio_user_props

        if user_props.is_logged == False:
            self.report({'INFO'},
                        TRADUCTOR['notif']['not_logged_in'][CONFIG_LANG])
            return {'CANCELLED'}

        if bpy.data.is_saved == False or bpy.data.is_dirty == True:
            self.report({'WARNING'},
                        TRADUCTOR['notif']['file_not_saved'][CONFIG_LANG])
            return {'CANCELLED'}

        print(f'RENDERING {self.render_type}')
        render = Render(bpy.data.filepath, 'my_render')
        asyncio.ensure_future(Renderer().upload_blend_file(render))
        async_loop.ensure_async_loop()

        return {'FINISHED'}
