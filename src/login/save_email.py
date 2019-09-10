from src.config import email_config_path
from src.utils.json import load_json, write_json

def remove_email_infos():
    try:
        open(email_config_path, 'w').close() # empty conf file
    except Exception as e:
        print(e)

## Returns the saved email
def email_from_conf():
        try:
            email_conf = load_json(email_config_path)
        except Exception as e:
            print(e)
            return ''
        if 'email' not in email_conf:
            remove_email_infos()
            return ''
        return email_conf['email']

def save_email_infos(email):
    conf = {
        'email': email,
    }
    try:
        write_json(conf, email_config_path)
    except Exception as e:
        print(e)
