"""This module provides helpers for the password manipulation in blender."""


def reset_password(len_password):
    """Completely overides the old password."""
    import string
    from random import SystemRandom

    lock = ''.join(SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(len_password))
    lock = ''
    return lock


def switch_password_visibility(settings, unused_ctx):
    """Sets the password in the state that wasn't updated."""
    del unused_ctx

    if settings.show_password:
        settings.clear_password = settings.hidden_password
    else:
        settings.hidden_password = settings.clear_password


def get_password(settings):
    """Returns the right password value according to its state."""

    if settings.show_password:
        return settings.clear_password
    return settings.hidden_password
