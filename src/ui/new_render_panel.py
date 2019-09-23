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
        render_form = bpy.context.window_manager.tresorio_render_form
        render_packs = bpy.context.window_manager.tresorio_render_packs
        report_props = bpy.context.window_manager.tresorio_report_props

        layout = self.layout

        # CONFIGURATION
        layout = layout.split(factor=0.020)
        layout.column()
        layout = layout.split(factor=0.980).column()
        layout.label(text=TRADUCTOR['field']['configuration'][CONFIG_LANG]+':')

        col = layout.column()

        box = col.box()

        row = box.row().split(factor=0.4)
        row.label(
            text=TRADUCTOR['field']['new_rendering_name'][CONFIG_LANG]+':')
        row.prop(render_form, 'rendering_name')

        row = box.row().split(factor=0.4)
        row.label(text=TRADUCTOR['field']['engine'][CONFIG_LANG]+':')
        row.prop(render_form, 'render_engines_list')

        row = box.row().split(factor=0.4)
        row.label(text=TRADUCTOR['field']['format'][CONFIG_LANG]+':')
        row.prop(render_form, 'output_formats_list')

        box = col.box()
        box.label(text=TRADUCTOR['field']['timeout'][CONFIG_LANG]+':')
        row = box.row().split(factor=0.15)
        row.label(icon='PREVIEW_RANGE')
        row.prop(render_form, 'timeout', text='Hours')

        box.row().label(text=TRADUCTOR['field']
                        ['render_pack'][CONFIG_LANG]+':')
        row = box.row()
        for pack in render_packs:
            row.prop(pack, 'is_selected', text=pack.name, toggle=1)

        box.label(text=TRADUCTOR['field']['render_type'][CONFIG_LANG]+':')
        box.row().prop_tabs_enum(render_form, 'render_types')

        row = box.row().split(factor=0.5)
        row.label(text='Max cost:')
        row.label(text=f'{render_form.max_cost:2.2f}€')

        # LAUNCH
        box = layout.box()
        box.enabled = not report_props.uploading_blend_file
        box.column().operator('tresorio.render_frame',
                              text=TRADUCTOR['field']['launch'][CONFIG_LANG],
                              icon='PLAY')

        if report_props.uploading_blend_file is True:
            layout.box().prop(render_form, 'upload_percent',
                              text=TRADUCTOR['desc']['uploading'][CONFIG_LANG])
            layout.separator(factor=0.3)
        if report_props.upload_failed is True:
            layout.box().label(text=TRADUCTOR['desc']['upload_failed'][CONFIG_LANG],
                               icon='ERROR')
            layout.separator(factor=0.3)
