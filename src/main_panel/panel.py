import bpy

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

            col = layout.row().split(factor=0.36)
            col.label(text="")
            col.label(text="Connection")

            layout.label(text="Mail")
            layout.prop(settings, "mail", text="")
            layout.label(text="Password:")

            row = layout.row().split(factor=0.9)
            if settings.show_password:
                row.prop(settings, "clear_password", text="")
            else:
                row.prop(settings, "hidden_password", text="")
            row.prop(settings, "show_password", icon_only=True, icon="HIDE_OFF")

            layout.separator(factor=0.1)

            row = layout.row().split(factor=0.3)
            row.column().prop(settings, "stay_connected", text="Stay connected")
            col = row.column()
            if settings.mail=="" or settings.hidden_password=="" and settings.clear_password=="":
                col.enabled=False
            col.operator("tresorio.login", icon='UNLOCKED', text='Login')

            layout.separator(factor=4.0)

            layout.operator("wm.url_open", text="Forgot your password ?", icon="QUESTION").url = "http://192.168.15.20:3000/password"
            layout.operator("wm.url_open", text="Create your account now", icon="PLUS").url = "http://192.168.15.20:3000/register"

            ## TODO Login panel, interface ...
        elif settings.is_logged == True:

            row = layout.row()
            row.label(text=settings.mail)
            row.operator("tresorio.logout", icon='LOCKED', text='Logout')
            #row.operator("tresorio.render", icon='RENDER_ANIMATION')