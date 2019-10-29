"""This module provides the tools for the language configurations."""

import src.utils.json_rw as json
import src.config.paths as paths
from src.config.user_json import USER_CONFIG

CONFIG_LANG = USER_CONFIG['lang']

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


def set_new_lang(settings, context):
    """Helper for blender to set the default language in the config file."""
    del context
    USER_CONFIG['lang'] = settings.langs
