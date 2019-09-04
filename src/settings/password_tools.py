def switch_password_visibility(settings, ctx):
    if settings.show_password:
        settings.clear_password = settings.hidden_password
    else:
        settings.hidden_password = settings.clear_password


def get_password(settings):
    if settings.show_password:
        return settings.clear_password
    else:
        return settings.hidden_password
