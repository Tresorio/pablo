import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioLogout(bpy.types.Operator):
    bl_idname = 'tresorio.logout'
    bl_label = 'Logout'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['tresorio_logout'][CONFIG_LANG]

    def execute(self, context):
        settings = context.scene.tresorio_settings

        if settings.is_logged == False:
            self.report({'INFO'},
                        TRADUCTOR['notif']['not_logged_in'][CONFIG_LANG])
            return {'CANCELLED'}

        context.scene.tresorio_settings.is_logged = False

        self.report({'INFO'},
                    TRADUCTOR['notif']['success_logout'][CONFIG_LANG])
        return {'FINISHED'}
