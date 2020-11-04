"""Defines the drawer for the connection panel"""

import bpy
from bundle_modules import i18n
from src.ui.icons import TresorioIconsLoader as til


def draw_connection_panel(layout: bpy.types.UILayout,
                          context: bpy.types.Context
                          ) -> None:
    """Draws the panel to connect to Tresorio"""
    user_props = context.window_manager.tresorio_user_props
    report_props = bpy.context.window_manager.tresorio_report_props

    case = layout.row().split(factor=0.5)
    case.label(text=i18n.t('blender.connection'))
    align_case = case.column().row().split(factor=0.8)
    align_case.column().prop(user_props, 'langs')
    align_case.column().operator('tresorio.advanced_settings_navigation_in',
                                 icon_value=til.icon('TRESORIO_SETTINGS'),
                                 text='')

    box = layout.box()
    box.label(text=i18n.t('blender.mail'))
    box.prop(user_props, 'email', text='')
    box.label(text=i18n.t('blender.password'))

    row = box.row().split(factor=0.9)
    if user_props.show_password:
        row.prop(user_props, 'clear_password', text='')
    else:
        row.prop(user_props, 'hidden_password', text='')
    row.prop(user_props, 'show_password',
             icon_only=True, icon='HIDE_OFF')

    row = layout.row().split(factor=0.5)
    row.column().prop(user_props, 'remember_email',
                      text=i18n.t('blender.remember-email'))
    col = row.column()
    if not report_props.login_in:
        col.operator('tresorio.login', icon_value=til.icon('TRESORIO_LOGIN'),
                     text=i18n.t('blender.login'))
    else:
        col.label(text=i18n.t('blender.login-in'))

    layout.separator(factor=2.0)

    layout.operator('tresorio.redirect_forgot_password',
                    text=i18n.t('blender.forgot-password'),
                    icon_value=til.icon('TRESORIO_KEY'))
    layout.operator('tresorio.redirect_register',
                    text=i18n.t('blender.create-account'),
                    icon_value=til.icon('TRESORIO_PROFILE'))
