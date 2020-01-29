"""This module defines the render frame operator"""

from typing import Set

from src.ui.popup import popup
from src.services.backend import new_render
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy

# pylint: disable=no-self-use


class TresorioRenderFrameOperator(bpy.types.Operator):
    """Render operator"""
    __doc__ = TRADUCTOR['desc']['tresorio_render'][CONFIG_LANG]
    bl_idname = 'tresorio.render'
    bl_label = 'Render frame'

    @classmethod
    def poll(cls,
             context: bpy.types.Context
             ) -> bool:
        """Wether to enable or disable the operator"""
        del cls
        return (context.window_manager.tresorio_user_props.is_logged and
                context.scene.tresorio_render_form.rendering_name)

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        user_props = context.window_manager.tresorio_user_props

        if not user_props.is_logged:
            popup(TRADUCTOR['notif']['not_logged_in']
                  [CONFIG_LANG], icon='ERROR')
            return {'CANCELLED'}

        new_render()

        return {'FINISHED'}
