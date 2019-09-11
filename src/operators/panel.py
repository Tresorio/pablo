import bpy
import urllib.parse as url
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioPanel(bpy.types.Panel):
    """Tresorio's blender plugin, un plugin qui chauffe plutot pas mal."""

    bl_label = 'Tresorio Rendering'
    bl_idname = 'OBJECT_PT_TRESORIO_PANEL'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    def draw(self, context):
        settings = context.scene.tresorio_settings

        if settings.is_logged == False:
            self.draw_connection_panel(settings)
        else:
            self.draw_rendering_panel(settings)

    def draw_rendering_panel(self, settings):
        """Draws the panel to use Tresorio's rendering"""
        layout = self.layout

        case = layout.row().grid_flow(columns=10)
        case.label(text=TRADUCTOR['field']['rendering'][CONFIG_LANG])
        align_case = case.row()
        align_case.column().prop(settings, 'langs')

        layout.operator('tresorio.render_frame',
                        text=TRADUCTOR['field']['render_frame'][CONFIG_LANG],
                        icon='RESTRICT_RENDER_OFF')
        layout.operator('tresorio.render_frame',
                        text=TRADUCTOR['field']['render_animation'][CONFIG_LANG],
                        icon='RENDER_ANIMATION')

        row = layout.row()
        row.label(text=settings.email)
        row.operator('tresorio.logout',
                     text=TRADUCTOR['field']['logout'][CONFIG_LANG],
                     icon='LOCKED')

    def draw_connection_panel(self, settings):
        """Draws the panel to connect to Tresorio"""
        layout = self.layout

        case = layout.row().grid_flow(columns=10)
        case.label(text=TRADUCTOR['field']['connection'][CONFIG_LANG])
        align_case = case.row()
        align_case.column().prop(settings, 'langs')

        box = layout.box()
        box.label(text=TRADUCTOR['field']['mail'][CONFIG_LANG])
        box.prop(settings, 'email', text='')
        box.label(text=TRADUCTOR['field']['password'][CONFIG_LANG])

        row = box.row().split(factor=0.9)
        if settings.show_password:
            row.prop(settings, 'clear_password', text='')
        else:
            row.prop(settings, 'hidden_password', text='')
        row.prop(settings, 'show_password',
                 icon_only=True, icon='HIDE_OFF')

        layout.separator(factor=0.1)

        row = layout.row().split(factor=0.5)
        row.column().prop(settings, 'remember_email',
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
