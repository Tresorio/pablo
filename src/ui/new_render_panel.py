"""Render creation panel"""

from src.config.langs import TRADUCTOR, CONFIG_LANG
import bpy


class TresorioNewRenderPanel(bpy.types.Panel):
    """Render creation panel"""
    bl_idname = 'OBJECT_PT_TRESORIO_NEW_RENDER_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_label = TRADUCTOR['field']['new_render_panel'][CONFIG_LANG]
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Chose wether to render the new render panel or not"""
        return (context.window_manager.tresorio_user_props.is_logged and
            not context.window_manager.tresorio_user_props.is_launching_rendering)

    def draw(self,
             context: bpy.types.Context
             ) -> None:
        """Draw the form required for a rendering"""
        render_form = context.scene.tresorio_render_form
        report_props = context.window_manager.tresorio_report_props

        layout = self.layout
        box = layout.box()

        # SETTINGS
        row = box.row()
        row_1 = row.row()
        row_1.alignment = 'LEFT'
        row_1.prop(render_form, 'show_settings', emboss=False,
                   text=TRADUCTOR['field']['settings'][CONFIG_LANG]+':')
        row_2 = row.row()
        row_2.alignment = 'RIGHT'
        icon = 'DISCLOSURE_TRI_DOWN' if render_form.show_settings else 'DISCLOSURE_TRI_RIGHT'
        row_2.prop(render_form, 'show_settings', text='', emboss=False,
                   icon=icon)

        if render_form.show_settings:
            row = box.row().split(factor=0.4)
            row.label(
                text=TRADUCTOR['field']['new_rendering_name'][CONFIG_LANG]+':')
            row.prop(render_form, 'rendering_name')

            row = box.row().split(factor=0.4)
            row.label(text=TRADUCTOR['field']['render_type'][CONFIG_LANG]+':')
            split = row.split(factor=0.5)
            split.prop(render_form, 'is_frame_selected', toggle=1,
                       text=TRADUCTOR['field']['frame'][CONFIG_LANG], icon='RESTRICT_RENDER_OFF')
            split.prop(render_form, 'is_animation_selected', toggle=1,
                       text=TRADUCTOR['field']['animation'][CONFIG_LANG], icon='RENDER_ANIMATION')

            row = box.row().split(factor=0.4)
            row.label(text=TRADUCTOR['field']['engine'][CONFIG_LANG]+':')
            row.prop_menu_enum(render_form, 'render_engines_list', icon='EMPTY_AXIS',
                               text=render_form.render_engines_list.capitalize())

            row = box.row().split(factor=0.4)
            row.label(text=TRADUCTOR['field']['format'][CONFIG_LANG]+':')
            row.prop_menu_enum(render_form, 'output_formats_list', icon='FILE_IMAGE',
                               text=render_form.output_formats_list)

            split = box.split(factor=0.4)
            split.label(text=TRADUCTOR['field']['options'][CONFIG_LANG]+':')
            grid_flow = split.grid_flow(
                even_rows=False, even_columns=True, align=True)

            grid_flow.prop(render_form, 'pack_textures',
                           text=TRADUCTOR['field']['pack_textures'][CONFIG_LANG])
            grid_flow.prop(render_form, 'auto_tile_size',
                           text=TRADUCTOR['field']['auto_tile_size'][CONFIG_LANG])
            grid_flow.prop(render_form, 'use_optix',
                            text=TRADUCTOR['field']['use_optix'][CONFIG_LANG])


        # LAUNCH
        is_ready_to_launch = False
        if context.window_manager.tresorio_report_props.deleting_all_renders:
            layout.label(text=TRADUCTOR['notif']
                         ['deleting_all_renders'][CONFIG_LANG])
        elif report_props.uploading_blend_file:
            box.prop(render_form, 'upload_percent',
                     text=TRADUCTOR['desc']['uploading'][CONFIG_LANG],
                     slider=True)
        elif report_props.packing_textures:
            box.label(text=TRADUCTOR['notif']['packing'][CONFIG_LANG])
        elif report_props.creating_render:
            box.label(text=TRADUCTOR['notif']['creating_render'][CONFIG_LANG])
        else:
            is_ready_to_launch = True
            box.operator('tresorio.upload')
        split = box.row().split()
        split.enabled = is_ready_to_launch
        split.operator('tresorio.cpurender')
        split.operator('tresorio.gpurender')