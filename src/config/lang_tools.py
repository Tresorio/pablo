from src.utils.json import load_json, write_json
import os.path as path
import bpy

## Config file
lang_config_path = path.join(bpy.utils.user_resource('CONFIG', path='tresorio', create=True), 'lang.json')

## Used for the EnumProperty
all_langs = {
    'eng': ('eng', 'eng_US', 'Set the language to English (US). You must restart Blender for the new language to be applied'),
    'fr':  ('fr', 'fr_FR', 'Définis le language à Français (FR). Vous devrez redémarrer Blender pour appliquer le nouveau language'),
}

def get_default_lang():
    try:
        lang_json = load_json(lang_config_path)
    except FileNotFoundError:
        return 'eng'
    if 'lang' not in lang_json:
        return 'eng'
    return lang_json['lang']

## Language used at addon loading
config_lang = get_default_lang()

def set_default_lang(lang):
    try:
        lang_json = load_json(lang_config_path)
    except FileNotFoundError:
        lang_json = {'lang': lang}
        write_json(lang_json, lang_config_path)
    else:
        lang_json['lang'] = lang
        write_json(lang_json, lang_config_path)

## Exposed utility function
def set_new_lang(settings, ctx):
    set_default_lang(settings.langs)
