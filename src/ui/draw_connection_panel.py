"""Defines the drawer for the connection panel"""

from src.ui.icons import TresorioIconsLoader as til
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy


def draw_connection_panel(layout: bpy.types.UILayout,
                          context: bpy.types.Context
                          ) -> None:
    """Draws the panel to connect to Tresorio"""
    user_props = context.window_manager.tresorio_user_props
    report_props = bpy.context.window_manager.tresorio_report_props

    case = layout.row().split(factor=0.5)
    case.label(text=TRADUCTOR['field']['connection'][CONFIG_LANG])
    align_case = case.column().row().split(factor=0.8)
    align_case.column().prop(user_props, 'langs')
    align_case.column().operator('tresorio.advanced_settings_navigation_in',
                                 icon_value=til.icon('TRESORIO_SETTINGS'),
                                 text='')

    box = layout.box()
    box.label(text=TRADUCTOR['field']['mail'][CONFIG_LANG] + ':')
    box.prop(user_props, 'email', text='')
    box.label(text=TRADUCTOR['field']['password'][CONFIG_LANG] + ':')

    row = box.row().split(factor=0.9)
    if user_props.show_password:
        row.prop(user_props, 'clear_password', text='')
    else:
        row.prop(user_props, 'hidden_password', text='')
    row.prop(user_props, 'show_password',
             icon_only=True, icon='HIDE_OFF')

    row = layout.row().split(factor=0.5)
    row.column().prop(user_props, 'remember_email',
                      text=TRADUCTOR['field']['remember_email'][CONFIG_LANG])
    col = row.column()
    if not report_props.login_in:
        col.operator('tresorio.login', icon_value=til.icon('TRESORIO_LOGIN'),
                     text=TRADUCTOR['field']['login'][CONFIG_LANG])
    else:
        col.label(text=TRADUCTOR['notif']['login_in'][CONFIG_LANG])

    layout.separator(factor=2.0)

    layout.operator('tresorio.redirect_forgot_password',
                    text=TRADUCTOR['field']['forgot_password'][CONFIG_LANG],
                    icon_value=til.icon('TRESORIO_KEY'))
    layout.operator('tresorio.redirect_register',
                    text=TRADUCTOR['field']['create_account'][CONFIG_LANG],
                    icon_value=til.icon('TRESORIO_PROFILE'))
