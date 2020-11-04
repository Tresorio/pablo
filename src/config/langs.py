"""This module provides the tools for the language configurations."""

from typing import Dict, Any

import bpy
from bundle_modules import i18n
from src.config.user_json import USER_CONFIG
from src.config import paths

CONFIG_LANG = USER_CONFIG['lang']

i18n.set('locale', CONFIG_LANG)
i18n.set('fallback', 'en')
i18n.set('file_format', 'json')
i18n.set('skip_locale_root_data', True)
i18n.load_path.append(paths.LANG_PATH)

ALL_LANGS = {
    'en': ('en',
           'English',
           i18n.t('blender.lang-select-warning', locale='en')),
    'fr':  ('fr',
            'Français',
            i18n.t('blender.lang-select-warning', locale='fr')),
}


def set_new_lang(settings: Dict[str, Any],
                 context: bpy.types.Context
                 ) -> None:
    """Helper for blender to set the default language in the config file."""
    del context
    USER_CONFIG['lang'] = settings.langs
    i18n.set('locale', USER_CONFIG['lang'])
