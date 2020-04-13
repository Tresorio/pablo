from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy

class ErrorPopup(bpy.types.Operator):
    bl_idname = "object.error_popup"
    bl_label = TRADUCTOR['desc']['something_went_wrong'][CONFIG_LANG]

    error_msg: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    subtitle: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def draw(self, context):
        self.layout.label(text=self.error_msg, icon="ERROR")
        if len(self.subtitle) != 0:
            self.layout.label(text=self.subtitle)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600, height=1000)

class InfoPopup(bpy.types.Operator):
    bl_idname = "object.info_popup"
    bl_label = TRADUCTOR['desc']['info'][CONFIG_LANG]

    info_msg: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def draw(self, context):
        self.layout.label(text=self.info_msg, icon="INFO")

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600, height=1000)
