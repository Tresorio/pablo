import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


def draw_connection_panel(layout: bpy.types.UILayout, context: bpy.types.Context):
    """Draws the panel to connect to Tresorio"""
    user_props = context.window_manager.tresorio_user_props

    case = layout.row().grid_flow(columns=10)
    case.label(text=TRADUCTOR['field']['connection'][CONFIG_LANG])
    align_case = case.row()
    align_case.column().prop(user_props, 'langs')

    layout.separator(factor=1.0)

    box = layout.box()
    box.label(text=TRADUCTOR['field']['mail'][CONFIG_LANG]+':')
    box.prop(user_props, 'email', text='')
    box.separator(factor=1.5)
    box.label(text=TRADUCTOR['field']['password'][CONFIG_LANG]+':')

    row = box.row().split(factor=0.9)
    if user_props.show_password:
        row.prop(user_props, 'clear_password', text='')
    else:
        row.prop(user_props, 'hidden_password', text='')
    row.prop(user_props, 'show_password',
             icon_only=True, icon='HIDE_OFF')

    layout.separator(factor=0.1)

    row = layout.row().split(factor=0.5)
    row.column().prop(user_props, 'remember_email',
                      text=TRADUCTOR['field']['remember_email'][CONFIG_LANG])
    col = row.column()
    col.operator('tresorio.login', icon='UNLOCKED',
                 text=TRADUCTOR['field']['login'][CONFIG_LANG])

    layout.separator(factor=4.0)

    layout.operator('tresorio.redirect_forgot_password',
                    text=TRADUCTOR['field']['forgot_password'][CONFIG_LANG],
                    icon='QUESTION')
    layout.operator('tresorio.redirect_register',
                    text=TRADUCTOR['field']['create_account'][CONFIG_LANG],
                    icon='PLUS')
