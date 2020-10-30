"""This module defines the advanced settings operator"""

from typing import Set

import bpy
from bundle_modules import i18n
from urllib.parse import urlparse
from src.ui.popup import popup
from src.services.tresorio_platform import set_backend_url
from src.config.api import API_CONFIG, MODE

# pylint: disable=too-few-public-methods,no-self-use


class TresorioAdvancedSettingsNavigationInOperator(bpy.types.Operator):
    """Advanced Settings Navigation operator"""
    __doc__ = i18n.t('blender.advanced-settings-navigation-in')
    bl_idname = 'tresorio.advanced_settings_navigation_in'
    bl_label = ''

    def execute(self, context: bpy.types.Context) -> Set[str]:
        """"Called when operator is called"""
        bpy.context.window_manager.tresorio_user_props.advanced_settings = True
        return {'FINISHED'}


class TresorioAdvancedSettingsNavigationOutOperator(bpy.types.Operator):
    """Advanced Settings Navigation operator"""
    __doc__ = i18n.t('blender.advanced-settings-navigation-out')
    bl_idname = 'tresorio.advanced_settings_navigation_out'
    bl_label = ''

    def execute(self, context: bpy.types.Context) -> Set[str]:
        """"Called when operator is called"""
        bpy.context.window_manager.tresorio_user_props.advanced_settings = False
        return {'FINISHED'}


class TresorioAdvancedSettingsOperator(bpy.types.Operator):
    """Advanced settings operator"""
    __doc__ = i18n.t('blender.save-advanced-settings')
    bl_idname = 'tresorio.advanced_settings'
    bl_label = 'Advanced settings'

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        user_props = context.window_manager.tresorio_user_props
        ip_address, port, https = user_props.backend_ip_address, user_props.backend_port, user_props.backend_https

        if ip_address == '':
            popup(i18n.t('blender.no-ip-address'), icon='ERROR')
            return {'CANCELLED'}

        new_url = "http"
        if https:
            new_url += 's'
        new_url += "://" + ip_address + ':' + port
        set_backend_url(new_url)

        bpy.context.window_manager.tresorio_user_props.advanced_settings = False

        return {'FINISHED'}


class TresorioAdvancedSettingsResetOperator(bpy.types.Operator):
    """Advanced settings reset operator"""
    __doc__ = i18n.t('blender.advanced-settings-reset')
    bl_idname = 'tresorio.advanced_settings_reset'
    bl_label = 'Advanced settings reset'

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""

        parsed_url = urlparse(API_CONFIG[MODE]['backend'])
        context.window_manager.tresorio_user_props.backend_ip_address = parsed_url.hostname
        if parsed_url.port:
            context.window_manager.tresorio_user_props.backend_port = str(parsed_url.port)
        else:
            context.window_manager.tresorio_user_props.backend_port = ''
        if parsed_url.scheme == 'https':
            context.window_manager.tresorio_user_props.backend_https = True
        else:
            context.window_manager.tresorio_user_props.backend_https = False

        set_backend_url(API_CONFIG[MODE]['backend'])

        return {'FINISHED'}
