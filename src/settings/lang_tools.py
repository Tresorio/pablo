from src.utils.json import load_json, write_json
from src.config import lang_config_path

def get_default_lang():
    try:
        lang_json = load_json(lang_config_path)
    except FileNotFoundError:
        return "eng"
    if "lang" not in lang_json:
        return "eng"
    return lang_json["lang"]

def set_default_lang(lang):
    try:
        lang_json = load_json(lang_config_path)
    except FileNotFoundError:
        pass
    lang_json["lang"] = lang
    write_json(lang_json, lang_config_path)
