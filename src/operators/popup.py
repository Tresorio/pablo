import bpy
from src.ui.popup import popup
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioPackDescriptionPopup(bpy.types.Operator):
    """This operator pops up a message describing the content of a render pack"""

    bl_idname = 'tresorio.pack_desc_popup'
    bl_label = ''

    msg: bpy.props.StringProperty(
        default='',
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    title: bpy.props.StringProperty(
        default='',
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    icon: bpy.props.StringProperty(
        default='NONE',
        options={'HIDDEN', 'SKIP_SAVE'}
    )
    icon_value: bpy.props.IntProperty(
        default=0,
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    @classmethod
    def set_doc(cls):
        cls.__doc__ = TRADUCTOR['desc']['pack_description_popup'][CONFIG_LANG]

    def execute(self, context):
        popup(msg=self.msg, title=self.title,
              icon=self.icon, icon_value=self.icon_value)
        return {'FINISHED'}
