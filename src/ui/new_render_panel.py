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
        box = layout.box()

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

        row = box.row().split(factor=0.4)
        row.label(text=TRADUCTOR['field']['timeout'][CONFIG_LANG]+':')
        row.prop(render_form, 'timeout',
                 text=TRADUCTOR['field']['hours'][CONFIG_LANG])

        row = box.row().split(factor=0.4)
        row.label(text=TRADUCTOR['field']['render_type'][CONFIG_LANG]+':')
        row.props_enum(render_form, 'render_types')

        box = box.split(factor=0.4)
        left = box.column() ; right = box.column()
        left.label(text=TRADUCTOR['field']['options'][CONFIG_LANG]+':')
        right.prop(render_form, 'pack_textures', text=TRADUCTOR['field']['pack_textures'][CONFIG_LANG])

        box = layout.box()
        box.row().label(text=TRADUCTOR['field']
                        ['render_pack'][CONFIG_LANG]+':')
        row = box.row()
        for pack in render_packs:
            row.prop(pack, 'is_selected', text=pack.name.upper(), toggle=1)
            if pack.is_selected is True:
                desc = pack.description.split('|')
                for line in desc:
                    box.label(text=line)

        row = layout.split(factor=0.3)
        row.label(text=TRADUCTOR['field']['max_cost'][CONFIG_LANG]+':')
        max_cost = render_form.max_cost - 0.005 if render_form.max_cost >= 0.005 else 0.0
        row.label(text=f'{max_cost:2.2f} ' +
                  TRADUCTOR['field']['credits'][CONFIG_LANG] +
                  f' ({render_form.max_timeout} h)')

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
