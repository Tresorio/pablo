from config.load_json import load_json
from config._local_paths import (_lang_description_path,
                                 _lang_field_path,
                                 _lang_notification_path,
                                 _tresorio_config_path)


lang_desc = load_json(_lang_description_path)
lang_field = load_json(_lang_field_path)
lang_notif = load_json(_lang_notification_path)

tresorio_config = load_json(_tresorio_config_path)
