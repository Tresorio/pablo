"""This module provides helpers for the password manipulation in blender."""

import string
from random import SystemRandom


def reset_password(len_password: int) -> str:
    """Completely overides the old password."""
    lock = ''.join(SystemRandom().choices(
        string.ascii_uppercase + string.digits, k=10))
    lock = ''
    return lock


def switch_password_visibility(settings, context):
    """Sets the password in the state that wasn't updated."""
    del context

    if settings.show_password:
        settings.clear_password = settings.hidden_password
    else:
        settings.hidden_password = settings.clear_password


def get_password(settings):
    """Returns the right password value according to its state."""
    if settings.show_password:
        return settings.clear_password
    return settings.hidden_password
