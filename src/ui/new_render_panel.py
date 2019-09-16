import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioNewRenderPanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_TRESORIO_NEW_RENDER_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_label = TRADUCTOR['field']['new_render_panel'][CONFIG_LANG]
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    @classmethod
    def poll(cls, context):
        return context.window_manager.tresorio_user_props.is_logged

    def draw(self, context: bpy.types.Context):
        """Draws the form required for a rendering"""

        layout = self.layout.box()
        form_fields = bpy.context.window_manager.tresorio_render_form

        col = layout.column()

        col.row().prop(form_fields, 'rendering_name',
                       text=TRADUCTOR['field']['new_rendering_name'][CONFIG_LANG])

        col.separator(factor=1.5)

        col.row().prop(form_fields, 'render_engines_list',
                       text=TRADUCTOR['field']['engine'][CONFIG_LANG])
        col.row().prop(form_fields, 'output_formats_list',
                       text=TRADUCTOR['field']['format'][CONFIG_LANG])

        col.separator(factor=1.5)

        row = col.row().split(factor=0.33)
        row.label(icon='PREVIEW_RANGE',
                           text=TRADUCTOR['field']['timeout'][CONFIG_LANG]+':')
        row.prop(form_fields, 'timeout', text='Hours')

        col.separator(factor=1.5)

        col.row().label(text=TRADUCTOR['field']['render_pack'][CONFIG_LANG]+':')
        col.row().prop_tabs_enum(form_fields, 'render_farms')

        col.separator(factor=1.5)

        row = layout.row()
        row.column().operator('tresorio.render_frame',
                              text=TRADUCTOR['field']['render_frame'][CONFIG_LANG],
                              icon='RESTRICT_RENDER_OFF').render_type = 'frame'
        row.column().operator('tresorio.render_frame',
                              text=TRADUCTOR['field']['render_animation'][CONFIG_LANG],
                              icon='RENDER_ANIMATION').render_type = 'animation'
