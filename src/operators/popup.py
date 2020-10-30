"""Popup window"""

import bpy
from bundle_modules import i18n

class ErrorPopup(bpy.types.Operator):
    bl_idname = "object.error_popup"
    bl_label = i18n.t('blender.something-went-wrong')

    error_msg: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    subtitle: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def draw(self, context):
        self.layout.label(text=self.error_msg, icon="ERROR")
        self.layout.label(text=self.subtitle)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=700)

class InfoPopup(bpy.types.Operator):
    bl_idname = "object.info_popup"
    bl_label = i18n.t('blender.info')

    info_msg: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def draw(self, context):
        self.layout.label(text=self.info_msg, icon="INFO")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=700)
