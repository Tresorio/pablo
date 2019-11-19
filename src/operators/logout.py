"""This module defines the logout operator"""

from typing import Set

from src.operators.async_loop import shutdown_loop
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy


def logout(context: bpy.types.Context) -> None:
    """Logouts the user properly"""
    shutdown_loop()
    context.window_manager.property_unset('tresorio_report_props')
    context.window_manager.property_unset('tresorio_render_packs')
    context.window_manager.property_unset('tresorio_renders_details')
    context.window_manager.property_unset('tresorio_user_props')

# pylint: disable=too-few-public-methods


class TresorioLogoutOperator(bpy.types.Operator):
    """Logout operator"""
    __doc__ = TRADUCTOR['desc']['tresorio_logout'][CONFIG_LANG]
    bl_idname = 'tresorio.logout'
    bl_label = 'Logout'

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        logout(context)
        self.report({'INFO'}, TRADUCTOR['notif']
                    ['success_logout'][CONFIG_LANG])
        return {'FINISHED'}
