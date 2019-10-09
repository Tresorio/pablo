import bpy
from src.ui.icons import TresorioIconsLoader as til
from src.config.langs import TRADUCTOR, CONFIG_LANG


def draw_connection_panel(layout: bpy.types.UILayout, context: bpy.types.Context):
    """Draws the panel to connect to Tresorio"""
    user_props = context.window_manager.tresorio_user_props
    report_props = bpy.context.window_manager.tresorio_report_props

    case = layout.row().grid_flow(columns=10)
    case.label(text=TRADUCTOR['field']['connection'][CONFIG_LANG],
               icon_value=til.icon('TRESORIO_TRESORIO'))
    align_case = case.row()
    align_case.column().prop(user_props, 'langs')

    box = layout.box()
    box.label(text=TRADUCTOR['field']['mail'][CONFIG_LANG]+':')
    box.prop(user_props, 'email', text='')
    box.label(text=TRADUCTOR['field']['password'][CONFIG_LANG]+':')

    row = box.row().split(factor=0.9)
    if user_props.show_password:
        row.prop(user_props, 'clear_password', text='')
    else:
        row.prop(user_props, 'hidden_password', text='')
    row.prop(user_props, 'show_password',
             icon_only=True, icon='HIDE_OFF')

    if report_props.invalid_logs is True:
        layout.label(text=TRADUCTOR['notif']
                     ['invalid_login'][CONFIG_LANG], icon='ERROR')

    row = layout.row().split(factor=0.5)
    row.column().prop(user_props, 'remember_email',
                      text=TRADUCTOR['field']['remember_email'][CONFIG_LANG])
    col = row.column()
    if report_props.login_in is False:
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
