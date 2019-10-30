import bpy
from src.config.enums import RenderStatus
from src.ui.icons import TresorioIconsLoader as til
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioRendersList(bpy.types.UIList):
    bl_idname = 'OBJECT_UL_TRESORIO_RENDERS_LIST'

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
            else:
                row.label(text=TRADUCTOR['notif']
                          ['finished_render'][CONFIG_LANG])


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
        report_props = context.scene.tresorio_report_props
        data = context.window_manager
        layout = self.layout

        nb_renders = len(data.tresorio_renders_details)
        rows = 1
        layout.template_list('OBJECT_UL_TRESORIO_RENDERS_LIST', 'The_List',
                             data, 'tresorio_renders_details',
                             data, 'tresorio_renders_list_index',
                             rows=rows, maxrows=nb_renders)

        row = layout.row()
        row.alignment = 'CENTER'
        if report_props.downloading_render_results is True:
            row.label(text=TRADUCTOR['notif']['downloading'][CONFIG_LANG])
