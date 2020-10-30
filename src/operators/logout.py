"""This module defines the logout operator"""

from typing import Set

import bpy
from bundle_modules import i18n
from src.operators.async_loop import shutdown_loop


def logout(context: bpy.types.Context) -> None:
    """Logouts the user properly"""
    shutdown_loop()
    context.window_manager.property_unset('tresorio_report_props')
    context.window_manager.property_unset('tresorio_farm_props')
    context.window_manager.property_unset('tresorio_renders_details')
    context.window_manager.property_unset('tresorio_user_props')

# pylint: disable=too-few-public-methods


class TresorioLogoutOperator(bpy.types.Operator):
    """Logout operator"""
    __doc__ = i18n.t('blender.tresorio-logout')
    bl_idname = 'tresorio.logout'
    bl_label = 'Logout'

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        logout(context)
        self.report({'INFO'}, i18n.t('blender.success-logout'))
        return {'FINISHED'}
