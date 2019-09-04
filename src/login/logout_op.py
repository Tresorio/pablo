import bpy


class TresorioLogout(bpy.types.Operator):
    """Logout of Tresorio"""
    bl_idname = 'tresorio.logout'
    bl_label = 'Logout'

    def execute(self, context):
        settings = context.scene.tresorio_settings

        if settings.is_logged == False:
            self.report({'INFO'}, "Can't log out if you're not logged in")
            return {'CANCELLED'}

        context.scene.tresorio_settings.is_logged = False
        self.report({'INFO'}, "Successfully logged out")
        return {'FINISHED'}
