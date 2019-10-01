import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioRendersList(bpy.types.UIList):
    bl_idname = 'OBJECT_UL_TRESORIO_RENDERS_LIST'

    def draw_item(self, context, layout, data, render, icon, active_data, active_propname, index):
        layout = layout.split(factor=0.05)
        if render.is_finished is True:
            layout.label(text='', icon='KEYTYPE_JITTER_VEC')
        else:
            layout.label(text='', icon='KEYTYPE_BREAKDOWN_VEC')

        layout = layout.split(factor=0.6)
        icon = 'RENDER_ANIMATION' if render.type == 'ANIMATION' else 'RESTRICT_RENDER_OFF'
        layout.label(text=render.name, icon=icon)
        row = layout.row(align=True)
        row.alignment = 'RIGHT'
        if render.is_finished is False:
            row.prop(render, 'progression')
            row.operator('tresorio.stop_render',
                         text='',
                         icon='CANCEL').index = index
        else:
            col = row.column()
            if context.window_manager.tresorio_report_props.downloading_render_results is True:
                col.enabled = False
            col.operator('tresorio.download_render_results',
                         text='',
                         icon='SORT_ASC').index = index
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
        if report_props.are_renders_refreshing is True:
            layout.label(text=TRADUCTOR['notif']['refreshing'][CONFIG_LANG])
        else:
            layout.operator('tresorio.refresh_renders',
                            text='', icon='FILE_REFRESH')
        layout.template_list('OBJECT_UL_TRESORIO_RENDERS_LIST', 'The_List',
                             data, 'tresorio_renders_details',
                             data, 'tresorio_renders_list_index',
                             rows=rows, maxrows=nb_renders)

        row = layout.row()
        row.alignment = 'CENTER'
        if report_props.downloading_render_results is True:
            row.label(text=TRADUCTOR['notif']['downloading'][CONFIG_LANG])
