"""This module provides helpers for the password manipulation in blender."""

from random import SystemRandom
import string

import bpy


def reset_password(len_password: int) -> str:
    """Completely overides the old password."""
    lock = ''.join(SystemRandom().choices(
        string.ascii_uppercase + string.digits, k=len_password))
    lock = ''
    return lock


def switch_password_visibility(user_props: 'TresorioUserProps',
                               context: bpy.types.Context
                               ) -> None:
    """Sets the password in the state that wasn't updated."""
    del context
    if user_props.show_password:
        user_props.clear_password = user_props.hidden_password
    else:
        user_props.hidden_password = user_props.clear_password


def get_password(user_props: 'TresorioUserProps') -> str:
    """Returns the right password value according to its state."""
    if user_props.show_password:
        return user_props.clear_password
    return user_props.hidden_password
