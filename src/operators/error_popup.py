import bpy

class ErrorPopup(bpy.types.Operator):
    bl_idname = "object.error_popup"
    bl_label = "Something went wrong"

    error_msg: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})

    def draw(self, context):
        self.layout.label(text=self.error_msg, icon="ERROR")

    def execute(self, context):
        self.report({'ERROR'}, self.error_msg)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600, height=1000)
