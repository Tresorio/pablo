import bpy
from src.config.enums import RenderStatus
from src.ui.icons import TresorioIconsLoader as til
from src.config.langs import TRADUCTOR, CONFIG_LANG
from src.ui.draw_selected_render import draw_selected_render


def select_all(list, context):
    renders = bpy.context.window_manager.tresorio_renders_details
    for render in renders:
        render.is_target = list.select_all


class TresorioRendersList(bpy.types.UIList):
    bl_idname = 'OBJECT_UL_TRESORIO_RENDERS_LIST'

    desc=TRADUCTOR['desc']['select_all_renders'][CONFIG_LANG]
    select_all: bpy.props.BoolProperty(
        name='',
        default=False,
        description=desc,
        options={'HIDDEN', 'SKIP_SAVE'},
        update=select_all,
    )

    def draw_filter(self, context, layout):
        layout.separator()
        row = layout.row()
        row.operator('tresorio.download_targeted_render_results',
                     text=TRADUCTOR['field']['download_targeted_results'][CONFIG_LANG],
                     icon='IMPORT')
        row.operator('tresorio.delete_targeted_renders',
                     text=TRADUCTOR['field']['delete_targeted_results'][CONFIG_LANG],
                     icon='TRASH')
        row.prop(self, 'select_all')
        layout.prop(context.window_manager.tresorio_user_settings_props,
                    'open_image_on_download',
                    text=TRADUCTOR['field']['open_image_on_download'][CONFIG_LANG])

    def draw_item(self, context, layout, data, render, icon, active_data, active_propname, index):
        split = layout.split(factor=0.05)

        # STATUS_ICON
        if render.status == RenderStatus.FINISHED:
            split.label(text='', icon='KEYTYPE_JITTER_VEC')
        elif render.status == RenderStatus.RUNNING:
            split.label(text='', icon='KEYTYPE_BREAKDOWN_VEC')
        elif render.status == RenderStatus.STOPPING:
            split.label(text='', icon_value=til.icon('TRESORIO_STOPPING'))
        elif render.status == RenderStatus.LAUNCHING:
            split.label(text='', icon_value=til.icon('TRESORIO_LAUNCHING'))
        icon = 'RENDER_ANIMATION' if render.type == 'ANIMATION' else 'RESTRICT_RENDER_OFF'
        split.label(text=render.name, icon=icon)

        # INFO_CASE
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        if render.status == RenderStatus.LAUNCHING:
            row.label(text=TRADUCTOR['notif']['launching'][CONFIG_LANG])
        if render.status == RenderStatus.RUNNING:
            row.prop(render, 'progression')
        if render.status == RenderStatus.STOPPING:
            row.label(text=TRADUCTOR['notif']['stopping'][CONFIG_LANG])
        if render.status == RenderStatus.FINISHED:
            if render.rendered_frames == 0:
                row.label(
                    text=TRADUCTOR['notif']['no_result_render'][CONFIG_LANG])
            elif render.downloading is True:
                row.label(text=TRADUCTOR['notif']['downloading'][CONFIG_LANG])

        # OPS_CASE
        if render.status == RenderStatus.RUNNING:
            row.operator('tresorio.stop_render', icon='X').index = index
        elif render.rendered_frames > 0 and render.status != RenderStatus.STOPPING:
            row.operator('tresorio.download_render_results',
                         text='',
                         icon='IMPORT').index = index
        if render.status != RenderStatus.STOPPING:
            row.operator('tresorio.delete_render',
                         text='',
                         icon='TRASH').index = index
            row.prop(render, 'is_target')


class TresorioRendersPanel(bpy.types.Panel):
    bl_label = TRADUCTOR['field']['your_renders'][CONFIG_LANG]
    bl_idname = 'OBJECT_PT_TRESORIO_RENDERS_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.window_manager.tresorio_user_props.is_logged

    def draw(self, context: bpy.types.Context):
        data = context.window_manager
        layout = self.layout

        nb_renders = len(data.tresorio_renders_details)
        layout.template_list('OBJECT_UL_TRESORIO_RENDERS_LIST', 'The_List',
                             data, 'tresorio_renders_details',
                             data, 'tresorio_renders_list_index',
                             rows=1, maxrows=nb_renders)

        user_settings = bpy.context.window_manager.tresorio_user_settings_props
        row = layout.row()
        row_1 = row.row()
        row_1.alignment = 'LEFT'
        row_1.prop(user_settings, 'show_selected_render', emboss=False,
                   text=TRADUCTOR['field']['selected_render_details'][CONFIG_LANG]+':',
                   icon='VIEWZOOM')
        row_2 = row.row()
        row_2.alignment = 'RIGHT'
        icon = 'DISCLOSURE_TRI_DOWN' if user_settings.show_selected_render else 'DISCLOSURE_TRI_RIGHT'
        row_2.prop(user_settings, 'show_selected_render', text='', emboss=False,
                   icon=icon)

        if bpy.context.window_manager.tresorio_user_settings_props.show_selected_render:
            draw_selected_render(layout, context)
