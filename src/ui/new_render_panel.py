"""Render creation panel"""

import bpy
from bundle_modules import i18n


class TresorioNewRenderPanel(bpy.types.Panel):
    """Render creation panel"""
    bl_idname = 'OBJECT_PT_TRESORIO_NEW_RENDER_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_label = i18n.t('blender.new-render-panel')
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        """Chose wether to render the new render panel or not"""
        return (context.window_manager.tresorio_user_props.is_logged and
            not context.window_manager.tresorio_user_props.is_launching_rendering and
            not context.window_manager.tresorio_user_props.is_resuming_rendering)

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
        row_1.prop(render_form, 'show_settings', emboss=False, text=i18n.t('blender.settings'))
        row_2 = row.row()
        row_2.alignment = 'RIGHT'
        icon = 'DISCLOSURE_TRI_DOWN' if render_form.show_settings else 'DISCLOSURE_TRI_RIGHT'
        row_2.prop(render_form, 'show_settings', text='', emboss=False, icon=icon)

        if render_form.show_settings:
            row = box.row().split(factor=0.4)
            row.label(text=i18n.t('blender.new-rendering-name'))
            row.prop(render_form, 'rendering_name')

            row = box.row().split(factor=0.4)
            row.label(text=i18n.t('blender.render-type'))
            split = row.split(factor=0.5)
            split.prop(render_form, 'is_frame_selected', toggle=1,
                       text=i18n.t('blender.frame'), icon='RESTRICT_RENDER_OFF')
            split.prop(render_form, 'is_animation_selected', toggle=1,
                       text=i18n.t('blender.animation'), icon='RENDER_ANIMATION')

            row = box.row().split(factor=0.4)
            row.label(text=i18n.t('blender.engine'))
            row.prop_menu_enum(render_form, 'render_engines_list', icon='EMPTY_AXIS',
                               text=render_form.render_engines_list.capitalize())

            row = box.row().split(factor=0.4)
            row.label(text=i18n.t('blender.format'))
            row.prop_menu_enum(render_form, 'output_formats_list', icon='FILE_IMAGE',
                               text=render_form.output_formats_list)

            split = box.split(factor=0.4)
            split.label(text=i18n.t('blender.options'))
            grid_flow = split.grid_flow(
                even_rows=False, even_columns=True, align=True)

            grid_flow.prop(render_form, 'auto_tile_size',
                           text=i18n.t('blender.auto-tile-size'))
            # grid_flow.prop(render_form, 'use_optix',
            #                 text=i18n.t('blender.use-optix'))


        # PROJECT
        box = layout.box()
        row = box.row()
        row_1 = row.row()
        row_1.alignment = 'LEFT'
        row_1.prop(render_form, 'show_project', emboss=False, text=i18n.t('blender.project'))
        row_2 = row.row()
        row_2.alignment = 'RIGHT'
        icon = 'DISCLOSURE_TRI_DOWN' if render_form.show_project else 'DISCLOSURE_TRI_RIGHT'
        row_2.prop(render_form, 'show_project', text='', emboss=False,
                   icon=icon)

        if render_form.show_project:
            project_name = box.row().split(factor=0.4, align=True)
            project_name.label(text=i18n.t('blender.project-name'))
            project_name.prop(render_form, 'project_name')

            box.row().label(text=i18n.t('blender.project-directory'))

            project_content = box.row().split(factor=0.7, align=True)

            project_dir = project_content.column()
            project_dir.prop(render_form, 'project_folder')

            project_actions = project_content.column()
            upload = project_actions.operator('tresorio.upload')


            if report_props.uploading:
                project_actions.enabled = False
                if report_props.uploading_blend_file:
                    if render_form.file_uploading == "":
                        row = box.row()
                        sub_box = row.box()
                        sub_box.scale_x = 0.5
                        sub_box.scale_y = 0.5
                        sub_box.label(text=i18n.t('blender.preparing-upload'))
                        row.operator('tresorio.cancelupload', icon='X')
                    else:
                        row = box.row()
                        row.prop(render_form, 'upload_percent',
                                 text=i18n.t('blender.uploading').format(render_form.file_uploading),
                                 slider=True)
                        row.operator('tresorio.cancelupload', icon='X')
                elif report_props.packing_textures:
                    row = box.row()
                    row.prop(render_form, 'pack_percent',
                             text=i18n.t('blender.exporting'),
                             slider=True)
                    row.operator('tresorio.cancelupload', icon='X')
                else:
                    row = box.row()
                    sub_box = row.box()
                    sub_box.scale_x = 0.5
                    sub_box.scale_y = 0.5
                    sub_box.label(text=i18n.t('blender.preparing-export'))
                    row.operator('tresorio.cancelupload', icon='X')

        # LAUNCH
        is_ready_to_launch = not report_props.uploading_blend_file
        split = layout.row().split()
        split.enabled = is_ready_to_launch
        split.operator('tresorio.cpurender')
        split.operator('tresorio.gpurender')