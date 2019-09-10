import os.path as path

_dirname = path.dirname(__file__)
_config_jsons_path = '../../config'

_lang_path = path.join(_dirname, _config_jsons_path, 'lang')
_lang_notification_path = path.join(_lang_path, 'notification.json')
_lang_description_path = path.join(_lang_path, 'description.json')
_lang_field_path = path.join(_lang_path, 'field.json')

_tresorio_path = path.join(_dirname, _config_jsons_path, 'tresorio')
_tresorio_config_path = path.join(_tresorio_path, 'config.json')
