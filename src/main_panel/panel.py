import bpy
import urllib.parse as url
from src.config import tresorio_config as tc
from src.config import lang_field as lf

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
        lang = settings.curr_lang

        if settings.is_logged == False:

            col = layout.row().split(factor=0.36)
            col.label(text="")
            col.label(text=lf['connection'][lang])

            layout.label(text=lf['mail'][lang])
            layout.prop(settings, "mail", text="")
            layout.label(text=lf['password'][lang])

            row = layout.row().split(factor=0.9)
            if settings.show_password:
                row.prop(settings, "clear_password", text="")
            else:
                row.prop(settings, "hidden_password", text="")
            row.prop(settings, "show_password", icon_only=True, icon="HIDE_OFF")

            layout.separator(factor=0.1)

            row = layout.row().split(factor=0.3)
            row.column().prop(settings, "stay_connected", text=lf['stay_connected'][lang])
            col = row.column()
            col.operator("tresorio.login", icon='UNLOCKED', text=lf['login'][lang])

            layout.separator(factor=4.0)

            layout.operator("wm.url_open",
                            text=lf['forgot_password'][lang],
                            icon="QUESTION").url=url.urljoin(tc['frontend'], tc['routes']['forgot_password'])
            layout.operator("wm.url_open",
                            text=lf['create_account'][lang],
                            icon="PLUS").url=url.urljoin(tc['frontend'], tc['routes']['register'])

            ## TODO Login panel, interface ...
        elif settings.is_logged == True:

            row = layout.row()
            row.label(text=settings.mail)
            row.operator("tresorio.logout", icon='LOCKED', text='Logout')
            #row.operator("tresorio.render", icon='RENDER_ANIMATION')