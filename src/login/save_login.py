from src.config import login_config_path
from src.utils.json import load_json, write_json

def remove_login_infos():
    try:
        open(login_config_path, 'w').close() # empty conf file
    except Exception as e:
        print(e)

## Returns false in case there is no valid login config file, either way it returns True and the email
def login_from_conf():
        try:
            login_conf = load_json(login_config_path)
        except FileNotFoundError:
            return (False, "")
        if "mail" not in login_conf or "token" not in login_conf:
            remove_login_infos()
            return (False, "")
        return (True, login_conf['mail'])

def save_login_infos(mail, token, context):
    conf = {
        "mail": mail,
        "token": token,
    }
    try:
        write_json(conf, login_config_path)
    except Exception as e:
        print(e)
