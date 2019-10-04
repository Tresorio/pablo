import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioRendersList(bpy.types.UIList):
    bl_idname = 'OBJECT_UL_TRESORIO_RENDERS_LIST'

    def draw_item(self, context, layout, data, render, icon, active_data, active_propname, index):
        layout = layout.split(factor=0.05)
        if render.status == 'FINISHED':
            layout.label(text='', icon='KEYTYPE_JITTER_VEC')
        elif render.status == 'RUNNING':
            layout.label(text='', icon='KEYTYPE_BREAKDOWN_VEC')
        elif render.status == 'STOPPING':
            layout.label(text='', icon='CANCEL')
        elif render.status == 'LAUNCHING':
            layout.label(text='', icon='FILE_REFRESH')

        layout = layout.split(factor=0.6)
        icon = 'RENDER_ANIMATION' if render.type == 'ANIMATION' else 'RESTRICT_RENDER_OFF'
        layout.label(text=render.name, icon=icon)
        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        if render.status == 'RUNNING':
            row.prop(render, 'progression')
            row.operator('tresorio.stop_render',
                         text='',
                         icon='X').index = index
        elif render.status == 'FINISHED':
            if context.window_manager.tresorio_report_props.downloading_render_results is True:
                row.enabled = False
            row.operator('tresorio.download_render_results',
                         text='',
                         icon='SORT_ASC').index = index
        elif render.status == 'STOPPING':
            row.label(text=TRADUCTOR['notif']['stopping'][CONFIG_LANG])
        elif render.status == 'LAUNCHING':
            row.label(text=TRADUCTOR['notif']['launching'][CONFIG_LANG])
        row.operator('tresorio.delete_render',
                     text='',
                     icon='TRASH').index = index


class TresorioRendersPanel(bpy.types.Panel):
    bl_label = TRADUCTOR['field']['your_renders'][CONFIG_LANG]
    bl_idname = 'OBJECT_PT_TRESORIO_RENDERS_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.window_manager.tresorio_user_props.is_logged

    def draw(self, context: bpy.types.Context):
        report_props = context.window_manager.tresorio_report_props
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
