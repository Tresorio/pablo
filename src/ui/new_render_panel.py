import bpy
from src.ui.icons import TresorioIconsLoader as til
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioNewRenderPanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_TRESORIO_NEW_RENDER_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_label = TRADUCTOR['field']['new_render_panel'][CONFIG_LANG]
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    @classmethod
    def poll(cls, context):
        return context.window_manager.tresorio_user_props.is_logged

    def draw(self, context: bpy.types.Context):
        """Draws the form required for a rendering"""
        render_form = bpy.context.scene.tresorio_render_form
        render_packs = bpy.context.window_manager.tresorio_render_packs
        report_props = bpy.context.scene.tresorio_report_props

        layout = self.layout
        box = layout.box()

        # LAUNCH
        if report_props.uploading_blend_file is True:
            box.prop(render_form, 'upload_percent',
                     text=TRADUCTOR['desc']['uploading'][CONFIG_LANG],
                     slider=True)
        elif report_props.packing_textures is True:
            box.label(text='Packing ...')
        elif report_props.unpacking_textures is True:
            box.label(text='Unpacking ...')
        else:
            box.operator('tresorio.render_frame',
                         text=TRADUCTOR['field']['launch'][CONFIG_LANG])

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

        if render_form.show_settings is True:
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

        # RENDER PACKS
        row = box.row()
        row_1 = row.row()
        row_1.alignment = 'LEFT'
        row_1.prop(render_form, 'show_packs', emboss=False,
                   text=TRADUCTOR['field']['render_pack'][CONFIG_LANG]+':')
        row_2 = row.row()
        row_2.alignment = 'RIGHT'
        icon = 'DISCLOSURE_TRI_DOWN' if render_form.show_packs else 'DISCLOSURE_TRI_RIGHT'
        row_2.prop(render_form, 'show_packs', text='', emboss=False,
                   icon=icon)

        if render_form.show_packs is True:
            description = ''
            packs_cols = box.column_flow(columns=len(render_packs), align=True)
            for pack in render_packs:
                case = packs_cols.box().split(factor=0.90)
                case.prop(pack, 'is_selected',
                          text=pack.name.capitalize(), toggle=1)
                case.operator('tresorio.pack_desc_popup', text='',
                              icon_value=til.icon('TRESORIO_QUESTION'),
                              emboss=False).msg = pack.description
                if pack.is_selected is True:
                    description = TRADUCTOR['desc']['pack_description'][CONFIG_LANG].format(
                        pack.cost * render_form.nb_farmers,
                        pack.gpu * render_form.nb_farmers,
                        pack.cpu * render_form.nb_farmers
                    )

            row = box.row().split(factor=0.4)
            row.label(text=TRADUCTOR['field']['nb_farmers'][CONFIG_LANG]+':')
            row.prop(render_form, 'nb_farmers')

            row = box.row().split(factor=0.4)
            row.label(text=TRADUCTOR['field']['timeout'][CONFIG_LANG]+':')
            row.prop(render_form, 'timeout',
                     text=TRADUCTOR['field']['hours'][CONFIG_LANG],
                     expand=True)

            box.label(text=description)

            row = box.row().split(factor=0.3)
            row.label(text=TRADUCTOR['field']['max_cost'][CONFIG_LANG]+':')
            max_cost = round(render_form.max_cost * 100) / 100
            row.label(text=f'{max_cost:.2f} ' +
                      TRADUCTOR['field']['credits'][CONFIG_LANG] +
                      f' ({render_form.max_timeout} h)')

        # LAUNCH
        if report_props.uploading_blend_file is True:
            box.prop(render_form, 'upload_percent',
                     text=TRADUCTOR['desc']['uploading'][CONFIG_LANG],
                     slider=True)
        elif report_props.packing_textures is True:
            box.label(text='Packing ...')
        elif report_props.unpacking_textures is True:
            box.label(text='Unpacking ...')
        else:
            box.operator('tresorio.render_frame',
                         text=TRADUCTOR['field']['launch'][CONFIG_LANG])
