import bpy
import urllib.parse as url
from src.config import (tresorio_config as tc,
                        lang_field as lf,
                        config_lang)


class TresorioPanel(bpy.types.Panel):
    """Tresorio's blender plugin, un plugin qui chauffe plutot pas mal."""
    bl_label = "Tresorio Rendering"
    bl_idname = "OBJECT_PT_TRESORIO_PANEL"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.tresorio_settings

        if settings.is_logged == False:

            case = layout.row().grid_flow(columns=10)
            case.label(text=lf['connection'][config_lang])
            align_case = case.row()
            align_case.column().prop(settings, "langs")

            box = layout.box()
            box.label(text=lf['mail'][config_lang])
            box.prop(settings, "email", text="")
            box.label(text=lf['password'][config_lang])

            row = box.row().split(factor=0.9)
            if settings.show_password:
                row.prop(settings, "clear_password", text="")
            else:
                row.prop(settings, "hidden_password", text="")
            row.prop(settings, "show_password",
                     icon_only=True, icon="HIDE_OFF")

            layout.separator(factor=0.1)

            row = layout.row().split(factor=0.5)
            row.column().prop(settings, "remember_email",
                              text=lf['remember_email'][config_lang])
            col = row.column()
            col.operator("tresorio.login", icon='UNLOCKED',
                         text=lf['login'][config_lang])

            layout.separator(factor=4.0)

            layout.operator("tresorio.redirect_forgot_password",
                            text=lf['forgot_password'][config_lang],
                            icon="QUESTION")
            layout.operator("tresorio.redirect_register",
                            text=lf['create_account'][config_lang],
                            icon="PLUS")

        elif settings.is_logged == True:

            case = layout.row().grid_flow(columns=10)
            case.label(text=lf['rendering'][config_lang])
            align_case = case.row()
            align_case.column().prop(settings, "langs")

            layout.operator('tresorio.render_frame',
                            text=lf['render_frame'][config_lang],
                            icon='RESTRICT_RENDER_OFF')
            layout.operator('tresorio.render_frame',
                            text=lf['render_animation'][config_lang],
                            icon='RENDER_ANIMATION')

            row = layout.row()
            row.label(text=settings.email)
            row.operator("tresorio.logout",
                         text=lf['logout'][config_lang],
                         icon='LOCKED')
