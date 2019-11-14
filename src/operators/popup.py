"""This module defines the popup for render packs description"""

from typing import Set

from src.ui.popup import popup
from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy

# pylint: disable=too-few-public-methods


class TresorioPackDescriptionPopup(bpy.types.Operator):
    """Pack descriptor operator"""
    __doc__ = TRADUCTOR['desc']['pack_description_popup'][CONFIG_LANG]

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

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        del context
        popup(msg=self.msg, title=self.title,
              icon=self.icon, icon_value=self.icon_value)
        return {'FINISHED'}
