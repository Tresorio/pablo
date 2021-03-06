"""This module defines the properties of a user"""

from src.config.user_json import USER_CONFIG
from src.utils.password import switch_password_visibility
from src.config.langs import set_new_lang, TRADUCTOR, CONFIG_LANG, ALL_LANGS
from collections.abc import Coroutine
from src.services.loggers import BACKEND_LOGGER
from src.services.tresorio_platform import Platform
import asyncio
from src.config.api import API_CONFIG, MODE
from urllib.parse import urlparse
import bpy

async def fetch_latest_version() -> str:
    latest_version = '0.0.0'
    try:
        async with Platform() as plt:
            res = await plt.req_latest_version()
            latest_version = await res.text()
    except Exception as err:
        BACKEND_LOGGER.error(err)
        popup_msg = TRADUCTOR['notif']['cant_connect_to_tresorio'][CONFIG_LANG]
        latest_version = f"{API_CONFIG['version']['major']}.{API_CONFIG['version']['minor']}.{API_CONFIG['version']['patch']}"
    return latest_version

class TresorioUserProps(bpy.types.PropertyGroup):
    """User properties"""
    is_logged: bpy.props.BoolProperty(
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
        default=False,
    )

    is_launching_rendering: bpy.props.BoolProperty(
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
        default=False,
    )

    is_resuming_rendering: bpy.props.BoolProperty(
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
        default=False,
    )

    rendering_mode: bpy.props.StringProperty(
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    latest_version: bpy.props.StringProperty(
        name='latest_version',
        options={'HIDDEN', 'SKIP_SAVE'},
        default=asyncio.get_event_loop().run_until_complete(fetch_latest_version()),
    )

    cookie: bpy.props.StringProperty(
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
        default='',
    )

    langs: bpy.props.EnumProperty(
        name='',
        items=(ALL_LANGS['en'], ALL_LANGS['fr']),
        update=set_new_lang,
        default=ALL_LANGS[CONFIG_LANG][0],
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    conf_email = USER_CONFIG['email']
    desc = TRADUCTOR['desc']['mail'][CONFIG_LANG]
    email: bpy.props.StringProperty(
        name='',
        description=desc,
        maxlen=128,
        options={'HIDDEN', 'SKIP_SAVE'},
        default=conf_email,
    )

    password = USER_CONFIG['password']
    desc = TRADUCTOR['desc']['password'][CONFIG_LANG]
    hidden_password: bpy.props.StringProperty(
        name='',
        description=desc,
        maxlen=128,
        default=password,
        subtype='PASSWORD',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['password'][CONFIG_LANG]
    clear_password: bpy.props.StringProperty(
        name='',
        description=desc,
        maxlen=128,
        default=password,
        subtype='NONE',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['toggle_password'][CONFIG_LANG]
    show_password: bpy.props.BoolProperty(
        name='',
        description=desc,
        default=False,
        update=switch_password_visibility,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    desc = TRADUCTOR['desc']['remember_email'][CONFIG_LANG]
    remember_email: bpy.props.BoolProperty(
        name='',
        description=desc,
        default=conf_email != '',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    total_credits: bpy.props.FloatProperty(
        name='',
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    storage_access_key: bpy.props.StringProperty(
        name='',
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    storage_secret_key: bpy.props.StringProperty(
        name='',
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    id: bpy.props.StringProperty(
        name='',
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    firstname: bpy.props.StringProperty(
        default='',
        name='',
        description='',
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    lastname: bpy.props.StringProperty(
        default='',
        name='',
        description='',
        update=lambda a, b: None,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    advanced_settings: bpy.props.BoolProperty(
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
        default=False,
    )

    parsed_url = urlparse(API_CONFIG[MODE]['backend'])
    backend_ip_address: bpy.props.StringProperty(
        default=parsed_url.hostname,
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    port = ''
    if parsed_url.port:
        port = str(parsed_url.port)
    backend_port: bpy.props.StringProperty(
        default=port,
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    https = False
    if parsed_url.scheme == 'https':
        https = True
    backend_https: bpy.props.BoolProperty(
        default=https,
        name='',
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    @classmethod
    def register(cls):
        """Link to window manager so these settings are reset at launch"""
        bpy.types.WindowManager.tresorio_user_props = bpy.props.PointerProperty(
            type=cls,
            name='tresorio_user_props',
            options={'HIDDEN', 'SKIP_SAVE'},
        )

    @classmethod
    def unregister(cls):
        """Unregister the class from blender"""
        del bpy.types.WindowManager.tresorio_user_props
