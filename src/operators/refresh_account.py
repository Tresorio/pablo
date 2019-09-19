import bpy
from src.services.backend import TresorioBackend
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioRefreshAccountOperator:
    bl_idname = 'tresorio.refresh_account'
    bl_label = 'Refresh Account'

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['tresorio_login'][CONFIG_LANG]

    def execute(self, context):

        return {'FINISHED'}