"""This module provides helpers for setting and getting email configuration."""

from src.config.paths import EMAIL_CONFIG_PATH
from . import json_rw as json


def remove_email_from_conf():
    """Empties the email configuration file."""

    try:
        with open(EMAIL_CONFIG_PATH, 'w') as file:
            file.write('{}')
    except OSError as exc:
        print(exc)


def get_email_from_conf():
    """Returns the email stored in the email configuration file, if any."""
    try:
        email_conf = json.load(EMAIL_CONFIG_PATH)
    except OSError as exc:
        print(exc)
        return ''
    if 'email' not in email_conf:
        remove_email_from_conf()
        return ''
    return email_conf['email']


def set_email_in_conf(email):
    """Sets the email value in the email configuration file."""

    conf = {'email': email}
    try:
        json.write(conf, EMAIL_CONFIG_PATH)
    except OSError as exc:
        print(exc)
