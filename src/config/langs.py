"""This module provides the tools for the language configurations."""

from . import paths
import src.utils.json_rw as json


def _get_default_lang():
    """Returns the default language if any was saved, either returns `en`."""

    try:
        lang_json = json.load(paths.LANG_CONFIG_PATH)
    except FileNotFoundError:
        return 'en'
    if 'lang' not in lang_json:
        return 'en'
    return lang_json['lang']

CONFIG_LANG = _get_default_lang()

TRADUCTOR = {
    'desc': json.load(paths.LANG_DESCRIPTION_PATH),
    'field': json.load(paths.LANG_FIELD_PATH),
    'notif': json.load(paths.LANG_NOTIFICATION_PATH),
}

ALL_LANGS = {
    'en': ('en-US',
            'English (US)',
            'Set the language to English (US). '
            'You must restart Blender for the new language to be applied'),
    'fr':  ('fr-FR',
            'Français (FR)',
            'Définir le language à Français (FR). '
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


def set_new_lang(settings, context):
    """Helper for blender to set the default language in the config file."""
    del context
    _set_default_lang(settings.langs)
