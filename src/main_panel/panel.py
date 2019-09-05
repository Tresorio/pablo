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
            box.prop(settings, "mail", text="")
            box.label(text=lf['password'][config_lang])

            row = box.row().split(factor=0.9)
            if settings.show_password:
                row.prop(settings, "clear_password", text="")
            else:
                row.prop(settings, "hidden_password", text="")
            row.prop(settings, "show_password", icon_only=True, icon="HIDE_OFF")

            layout.separator(factor=0.1)

            row = layout.row().split(factor=0.5)
            row.column().prop(settings, "stay_connected", text=lf['stay_connected'][config_lang])
            col = row.column()
            col.operator("tresorio.login", icon='UNLOCKED', text=lf['login'][config_lang])

            layout.separator(factor=4.0)

            layout.operator("wm.url_open",
                            text=lf['forgot_password'][config_lang],
                            icon="QUESTION").url=url.urljoin(tc['frontend'], tc['routes']['forgot_password'])
            layout.operator("wm.url_open",
                            text=lf['create_account'][config_lang],
                            icon="PLUS").url=url.urljoin(tc['frontend'], tc['routes']['register'])

            ## TODO Login panel, interface ...
        elif settings.is_logged == True:

            case = layout.row().grid_flow(columns=10)
            case.label(text=lf['rendering'][config_lang])
            align_case = case.row()
            align_case.column().prop(settings, "langs")

            row = layout.row()
            row.label(text=settings.mail)
            row.operator("tresorio.logout", icon='LOCKED', text=lf['logout'][config_lang])
