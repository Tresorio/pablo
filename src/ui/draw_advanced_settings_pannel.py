"""Defines the drawer for the connection panel"""

import bpy
from bundle_modules import i18n
from src.config.api import API_CONFIG


def draw_advanced_settings_panel(layout: bpy.types.UILayout,
                                 context: bpy.types.Context
                                 ) -> None:
    """Draws the advanced settings panel"""
    user_props = context.window_manager.tresorio_user_props

    case = layout.row().split(factor=0.5)
    case.label(text=i18n.t('blender.advanced-settings'))
    case = case.row().split(factor=0.7)
    case.operator('tresorio.advanced_settings_reset',
                  text=i18n.t('blender.reset-advanced-settings'),
                  icon='MODIFIER')
    case.operator('tresorio.advanced_settings_navigation_out',
                  text='',
                  icon='CANCEL')

    latest_version = user_props.latest_version
    actual_version = f"{API_CONFIG['version']['major']}.{API_CONFIG['version']['minor']}.{API_CONFIG['version']['patch']}"
    box = layout.split(factor=0.5).box()
    box.enabled = False
    box.scale_x = 0.5
    box.scale_y = 0.5
    # TODO fix that ugly thing
    box.label(text=i18n.t('blender.version') + " : " + actual_version)
    box.label(text=i18n.t('blender.latest') + " : " + latest_version)

    box = layout.box()
    split = box.split(factor=0.4, align=True)
    split.alignment = 'RIGHT'
    split.label(text=i18n.t('blender.backend-ip'))
    split.prop(user_props, 'backend_ip_address', text='')

    split = box.split(factor=0.4)
    split.alignment = 'RIGHT'
    split.label(text=i18n.t('blender.backend-port'))
    split.prop(user_props, 'backend_port', text='')

    split = box.split(factor=0.4)
    split.alignment = 'RIGHT'
    split.label(text=i18n.t('blender.backend-https'))
    split.prop(user_props, 'backend_https', text='')

    layout.operator('tresorio.advanced_settings',
                    icon='CHECKMARK',
                    text=i18n.t('blender.save-settings'))
