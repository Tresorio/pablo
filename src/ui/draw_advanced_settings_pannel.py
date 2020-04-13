"""Defines the drawer for the connection panel"""

from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.config.api import API_CONFIG
import bpy


def draw_advanced_settings_panel(layout: bpy.types.UILayout,
                                 context: bpy.types.Context
                                 ) -> None:
    """Draws the advanced settings panel"""
    user_props = context.window_manager.tresorio_user_props

    case = layout.row().split(factor=0.5)
    case.label(text=TRADUCTOR['field']['advanced_settings'][CONFIG_LANG])
    case = case.row().split(factor=0.7)
    case.operator('tresorio.advanced_settings_reset',
                  text=TRADUCTOR['field']['reset_advanced_settings'][CONFIG_LANG],
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
    box.label(text=TRADUCTOR['field']['version'][CONFIG_LANG] + " : " + actual_version)
    box.label(text=TRADUCTOR['field']['latest'][CONFIG_LANG] + " : " + latest_version)

    box = layout.box()
    split = box.split(factor=0.4, align=True)
    split.alignment = 'RIGHT'
    split.label(text=TRADUCTOR['field']['backend_ip'][CONFIG_LANG])
    split.prop(user_props, 'backend_ip_address', text='')

    split = box.split(factor=0.4)
    split.alignment = 'RIGHT'
    split.label(text=TRADUCTOR['field']['backend_port'][CONFIG_LANG])
    split.prop(user_props, 'backend_port', text='')

    split = box.split(factor=0.4)
    split.alignment = 'RIGHT'
    split.label(text=TRADUCTOR['field']['backend_https'][CONFIG_LANG])
    split.prop(user_props, 'backend_https', text='')

    layout.operator('tresorio.advanced_settings',
                    icon='CHECKMARK',
                    text=TRADUCTOR['field']['save_settings'][CONFIG_LANG])
