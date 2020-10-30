"""Draw the renders details of the user"""

import bpy
from bundle_modules import i18n
from src.config.enums import RenderStatus
from src.ui.icons import TresorioIconsLoader as til
from src.ui.draw_selected_render import draw_selected_render
from src.properties.renders import TresorioRendersDetailsProps


class TresorioRendersList(bpy.types.UIList):
    """The ui list of renders"""
    bl_idname = 'OBJECT_UL_TRESORIO_RENDERS_LIST'

    @staticmethod
    def draw_filter(unused_self,
                    context: bpy.types.Context,
                    layout: bpy.types.UILayout
                    ) -> None:
        """Draw the filter part of the ui list"""
        del unused_self
        user_settings = context.window_manager.tresorio_user_settings_props
        layout.separator()
        # layout.prop(user_settings,
        #             'decompress_results',
        #             text=i18n.t('blender.decompress-results'))
        row = layout.row()
        if user_settings.decompress_results is False:
            row.enabled = False
        row.prop(user_settings,
                 'open_image_on_download',
                 text=i18n.t('blender.open-image-on-download'))

    # pylint: disable=too-many-arguments
    @staticmethod
    def draw_item(unused_self,
                  context: bpy.types.Context,
                  layout: bpy.types.UILayout,
                  data: bpy.types.WindowManager,
                  render: TresorioRendersDetailsProps,
                  icon: int,
                  active_data: bpy.types.WindowManager,
                  active_propname: str,
                  index: int
                  ) -> None:
        """Draw one element in the ui list"""
        del unused_self, context, data, active_data, active_propname

        split = layout.split(factor=0.05)
        # STATUS_ICON
        if render.status == RenderStatus.FINISHED:
            split.label(text='', icon='KEYTYPE_JITTER_VEC')
        elif render.status == RenderStatus.RUNNING:
            split.label(text='', icon='KEYTYPE_BREAKDOWN_VEC')
        elif render.status == RenderStatus.STOPPING or render.status == RenderStatus.STOPPED:
            split.label(text='', icon_value=til.icon('TRESORIO_STOPPING'))
        elif render.status == RenderStatus.STARTING:
            split.label(text='', icon_value=til.icon('TRESORIO_LAUNCHING'))
        elif render.status == RenderStatus.ERROR:
            split.label(text='', icon='KEYTYPE_KEYFRAME_VEC')
        icon = 'RENDER_ANIMATION' if render.type == 'ANIMATION' else 'RESTRICT_RENDER_OFF'
        split.label(text=render.name, icon=icon)

        # INFO_CASE
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        if render.downloading:
            row.label(text=i18n.t('blender.downloading'))
        elif render.status == RenderStatus.STARTING:
            row.label(text=i18n.t('blender.launching'))
        elif render.status == RenderStatus.RUNNING or render.status == RenderStatus.STOPPED:
            row.prop(render, 'progress')
        elif render.status == RenderStatus.STOPPING:
            row.label(text=i18n.t('blender.stopping'))

        # OPS_CASE
        if render.is_downloadable:
            row.operator('tresorio.download_render_results',
                         text='',
                         icon='IMPORT').index = index
        if render.is_resumable:
            row.operator('tresorio.resume_render', icon='PLAY').index = index
        if render.is_restartable:
            row.operator('tresorio.resume_render', icon='FILE_REFRESH').index = index
        if render.is_stoppable:
            row.operator('tresorio.stop_render', icon='PAUSE').index = index
        row.operator('tresorio.delete_render',
                     text='',
                     icon='TRASH').index = index


class TresorioRendersPanel(bpy.types.Panel):
    """Renders details panel"""
    bl_label = i18n.t('blender.your-renders')
    bl_idname = 'OBJECT_PT_TRESORIO_RENDERS_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    @classmethod
    def poll(cls,
             context: bpy.types.Context
             ) -> bool:
        """Chose wether to render the renders panel or not"""
        return (context.window_manager.tresorio_user_props.is_logged and
            not context.window_manager.tresorio_user_props.is_launching_rendering and
            not context.window_manager.tresorio_user_props.is_resuming_rendering)

    def draw(self,
             context: bpy.types.Context
             ) -> None:
        """Draw the form required for a rendering"""
        data = context.window_manager
        layout = self.layout

        nb_renders = len(data.tresorio_renders_details)
        layout.template_list('OBJECT_UL_TRESORIO_RENDERS_LIST',
                             'The_List',
                             data,
                             'tresorio_renders_details',
                             data,
                             'tresorio_renders_list_index',
                             rows=1,
                             maxrows=nb_renders)

        user_settings = context.window_manager.tresorio_user_settings_props
        row = layout.row()
        row_1 = row.row()
        row_1.alignment = 'LEFT'

        icon = None
        if user_settings.show_selected_render:
            icon = 'DISCLOSURE_TRI_DOWN'
        else:
            icon = 'DISCLOSURE_TRI_RIGHT'

        row_1.prop(user_settings,
                   'show_selected_render',
                   emboss=False,
                   text=i18n.t('blender.selected-render-details')+':',
                   icon=icon)

        if data.tresorio_user_settings_props.show_selected_render:
            draw_selected_render(layout, context)
