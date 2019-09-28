import bpy
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioRendersList(bpy.types.UIList):
    bl_idname = 'OBJECT_UL_TRESORIO_RENDERS_LIST'

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        icon = 'RENDER_ANIMATION' if item.type == 'ANIMATION' else 'RESTRICT_RENDER_OFF'
        layout.label(text=item.name, icon=icon)
        layout.operator('tresorio.redirect_home',
                        text='Tresorio',
                        icon='INFO')


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
        data = context.window_manager
        layout = self.layout

        layout.template_list('OBJECT_UL_TRESORIO_RENDERS_LIST', 'The_List',
                             data, 'tresorio_renders_details',
                             data, 'renders_list_index',
                             rows=3, maxrows=len(data.tresorio_renders_details))
