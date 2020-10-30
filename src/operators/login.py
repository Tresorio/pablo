"""This module defines the login operator"""

from typing import Set

import bpy
from bundle_modules import i18n
from src.ui.popup import popup
from src.config.user_json import USER_CONFIG
from src.services.backend import connect_to_tresorio
from src.utils.password import reset_password, get_password

# pylint: disable=too-few-public-methods,no-self-use


class TresorioLoginOperator(bpy.types.Operator):
    """Login operator"""
    __doc__ = i18n.t('blender.tresorio-login')
    bl_idname = 'tresorio.login'
    bl_label = 'Login'

    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """Called when operator is called"""
        user_props = context.window_manager.tresorio_user_props
        email, password = user_props.email, get_password(user_props)
        context.window_manager.tresorio_user_props.hidden_password = reset_password(
            len(password))
        context.window_manager.tresorio_user_props.clear_password = reset_password(
            len(password))

        if user_props.is_logged:
            popup(i18n.t('blender.already-logged-in'), icon='ERROR')
            return {'CANCELLED'}
        if email == '' and password == '':
            popup(i18n.t('blender.no-mail-password'), icon='ERROR')
            return {'CANCELLED'}
        if email == '':
            popup(i18n.t('blender.no-mail'), icon='ERROR')
            return {'CANCELLED'}
        if password == '':
            popup(i18n.t('blender.no-password'), icon='ERROR')
            return {'CANCELLED'}

        if user_props.remember_email:
            USER_CONFIG['email'] = email
            USER_CONFIG['password'] = password
        else:
            USER_CONFIG['email'] = ''
            user_props.email = ''
            USER_CONFIG['password'] = ''
            user_props.email = ''
            user_props.hidden_password = ''
            user_props.clear_password = ''

        connect_to_tresorio(email, password)

        return {'FINISHED'}
