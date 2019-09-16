"""This module provides the operators achieving redirection to web browsers"""

from urllib.parse import urljoin
import logging
import bpy
from src.config.api import API_CONFIG
from src.config.langs import TRADUCTOR, CONFIG_LANG


class RedirectorOperator(bpy.types.Operator):
    """Base class for redirection operators. DON'T REGISTER."""

    def __init__(self):
        self.logger = logging.getLogger('Redirector')

    def execute(self, unused_ctx):
        """On click function"""
        del unused_ctx
        import webbrowser

        try:
            webbrowser.open_new_tab(self.url)
        except webbrowser.Error as exc:
            self.logger.error(exc)
            return {'CANCELLED'}

        return {'FINISHED'}


class TresorioRedirectForgotPasswordOperator(RedirectorOperator):
    """This operator redirects to the password recovery page Tresorio's website."""

    bl_idname = 'tresorio.redirect_forgot_password'
    bl_label = 'Forgot password'

    def __init__(self):
        super().__init__()
        self.url = urljoin(API_CONFIG['frontend'],
                           API_CONFIG['routes']['forgot_password'])

    @classmethod
    def set_doc(cls):
        """Customizes the docstring for Blender language management."""
        cls.__doc__ = TRADUCTOR['desc']['forgot_password'][CONFIG_LANG]


class TresorioRedirectRegisterOperator(RedirectorOperator):
    """This operator redirects to the registration page on the Tresorio's website."""

    bl_idname = 'tresorio.redirect_register'
    bl_label = 'Register'

    def __init__(self):
        super().__init__()
        self.url = urljoin(API_CONFIG['frontend'],
                           API_CONFIG['routes']['register'])

    @classmethod
    def set_doc(cls):
        """Customizes the docstring for Blender language management."""
        cls.__doc__ = TRADUCTOR['desc']['create_account'][CONFIG_LANG]


class TresorioRedirectHomeOperator(RedirectorOperator):
    """This operator redirects to the main page on the Tresorio's website."""

    bl_idname = 'tresorio.redirect_home'
    bl_label = 'Tresorio Home'

    def __init__(self):
        super().__init__()
        self.url = API_CONFIG['homepage']

    @classmethod
    def set_doc(cls):
        """Customizes the docstring for Blender language management."""
        cls.__doc__ = TRADUCTOR['desc']['redirect_tresorio'][CONFIG_LANG]
