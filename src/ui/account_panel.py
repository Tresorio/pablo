import bpy
from src.ui.icons import TresorioIconsLoader as til
from src.config.langs import TRADUCTOR, CONFIG_LANG


class TresorioAccountPanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_TRESORIO_ACCOUNT_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_label = TRADUCTOR['field']['account_panel'][CONFIG_LANG]
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.window_manager.tresorio_user_props.is_logged

    def draw(self, context: bpy.types.Context):
        """Draws the account informations"""
        user_props = context.window_manager.tresorio_user_props
        layout = self.layout

        case = layout.row().grid_flow(columns=10)
        case.label(text=user_props.email)
        align_case = case.row()
        align_case.column().prop(user_props, 'langs')

        split = layout.split(factor=0.5)
        rounded_credits = round(user_props.total_credits * 100) / 100
        split.label(text=f'Credits: {rounded_credits:.2f}')
        split.operator('tresorio.redirect_get_credits',
                        text=TRADUCTOR['field']['get_credits'][CONFIG_LANG],
                        icon_value=til.icon('TRESORIO_GET_CREDITS'))
        layout.operator('tresorio.logout',
                        text=TRADUCTOR['field']['logout'][CONFIG_LANG],
                        icon_value=til.icon('TRESORIO_LOGOUT'))
        layout.operator('tresorio.redirect_home',
                        text='Tresorio',
                        icon_value=til.icon('TRESORIO_LEAF'))
