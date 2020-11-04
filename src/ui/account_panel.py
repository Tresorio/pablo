"""This module defines the user account information panel"""

import bpy
from bundle_modules import i18n
from src.ui.icons import TresorioIconsLoader as til


class TresorioAccountPanel(bpy.types.Panel):
    """User account panel"""
    bl_idname = 'OBJECT_PT_TRESORIO_ACCOUNT_PANEL'
    bl_parent_id = 'OBJECT_PT_TRESORIO_PANEL'
    bl_label = i18n.t('blender.account-panel')
    bl_options = {'DEFAULT_CLOSED'}
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
        """Draws the account informations"""
        user_props = context.window_manager.tresorio_user_props
        layout = self.layout

        case = layout.row().grid_flow(columns=10)
        case.label(text=user_props.email)
        align_case = case.row()
        align_case.column().prop(user_props, 'langs')

        split = layout.split(factor=0.5)

        credits_round_precision = 2 if user_props.total_credits > 1 else 4
        split.label(text=i18n.t('blender.account-credits', credits=round(user_props.total_credits, credits_round_precision)))
        split.operator('tresorio.redirect_get_credits',
                       text=i18n.t('blender.get-credits'),
                       icon_value=til.icon('TRESORIO_GET_CREDITS'))
        layout.operator('tresorio.logout',
                        text=i18n.t('blender.logout'),
                        icon_value=til.icon('TRESORIO_LOGOUT'))
        layout.operator('tresorio.redirect_home',
                        text='Tresorio',
                        icon_value=til.icon('TRESORIO_LEAF'))
