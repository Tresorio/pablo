import bpy
import os.path as path
from src.utils.json import load_json
from .lang_tools import set_new_lang, config_lang, all_langs
from ._local_paths import (_lang_description_path,
                                 _lang_field_path,
                                 _lang_notification_path,
                                 _tresorio_config_path)


# To handle languages
lang_desc = load_json(_lang_description_path)
lang_field = load_json(_lang_field_path)
lang_notif = load_json(_lang_notification_path)



# Keeps all the informations relative to the tresorio apis
tresorio_config = load_json(_tresorio_config_path)

# Keeps mail and jwt token for future connections
login_config_path = path.join(bpy.utils.user_resource('CONFIG', path='tresorio', create=True), "login.json")
