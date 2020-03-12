"""Defines the drawer for the connection panel"""

from src.config.langs import TRADUCTOR, CONFIG_LANG
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
