"""This module provides the tools for the language configurations."""

from . import paths
import src.utils.json_rw as json


def _get_default_lang():
    """Returns the default language if any was saved, either returns `eng`."""

    try:
        lang_json = json.load(paths.LANG_CONFIG_PATH)
    except FileNotFoundError:
        return 'eng'
    if 'lang' not in lang_json:
        return 'eng'
    return lang_json['lang']

CONFIG_LANG = _get_default_lang()

TRADUCTOR = {
    'desc': json.load(paths.LANG_DESCRIPTION_PATH),
    'field': json.load(paths.LANG_FIELD_PATH),
    'notif': json.load(paths.LANG_NOTIFICATION_PATH),
}

ALL_LANGS = {
    'eng': ('eng',
            'English (US)',
            'Set the language to English (US). '
            'You must restart Blender for the new language to be applied'),
    'fr':  ('fr',
            'Français (FR)',
            'Définis le language à Français (FR). '
            'Vous devrez redémarrer Blender pour appliquer le nouveau language'),
}


def _set_default_lang(lang):
    """Sets the default language in the lang configuration file."""

    try:
        lang_json = json.load(paths.LANG_CONFIG_PATH)
    except FileNotFoundError:
        lang_json = {'lang': lang}
        json.write(lang_json, paths.LANG_CONFIG_PATH)
    else:
        lang_json['lang'] = lang
        json.write(lang_json, paths.LANG_CONFIG_PATH)


def set_new_lang(settings, unused_ctx):
    """Helper for blender to set the default language in the config file."""

    del unused_ctx
    _set_default_lang(settings.langs)
