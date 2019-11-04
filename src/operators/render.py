import os
import bpy
import asyncio
from src.ui.popup import popup
from src.services.backend import new_render
import src.services.async_loop as async_loop
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioRenderFrameOperator(bpy.types.Operator):
    bl_idname = 'tresorio.render_frame'
    bl_label = 'Render frame'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['tresorio_render'][CONFIG_LANG]

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return (context.window_manager.tresorio_user_props.is_logged and
                context.scene.tresorio_render_form.rendering_name)

    def execute(self, context):
        user_props = context.window_manager.tresorio_user_props

        if user_props.is_logged == False:
            popup(TRADUCTOR['notif']['not_logged_in']
                  [CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        if bpy.data.is_saved == False or bpy.data.is_dirty == True:
            popup(TRADUCTOR['notif']['file_not_saved']
                  [CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        new_render()

        return {'FINISHED'}
