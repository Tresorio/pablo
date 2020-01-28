"""Entrypoint of the addon"""

import os
import sys
import atexit
import asyncio
import bpy

# Add the path of the addon to python's sys path
USER_PATH = bpy.utils.resource_path('USER')
ADDON_PATH = os.path.join(USER_PATH, 'scripts', 'addons', 'tresorio')
MODULES_PATH = os.path.join(ADDON_PATH, 'bundle_modules')
sys.path.append(ADDON_PATH)
sys.path.append(MODULES_PATH)

# pylint: disable=wrong-import-position
import src
from src.ui.icons import TresorioIconsLoader
from src.properties.user_props import TresorioUserProps
from src.properties.report_props import TresorioReportProps
from src.properties.render_form import TresorioRenderFormProps
from src.properties.renders import TresorioRendersDetailsProps
from src.properties.render_packs import TresorioRenderPacksProps
from src.properties.user_settings import TresorioUserSettingsProps
from src.ui.main_panel import TresorioMainPanel
from src.ui.account_panel import TresorioAccountPanel
from src.ui.new_render_panel import TresorioNewRenderPanel
from src.ui.user_renders_panel import TresorioRendersPanel, TresorioRendersList
from src.operators.login import TresorioLoginOperator
from src.operators.logout import TresorioLogoutOperator
from src.operators.upload import TresorioUploadOperator
from src.operators.render import TresorioRenderFrameOperator
from src.operators.redirect import TresorioRedirectHomeOperator
from src.operators.stop_render import TresorioStopRenderOperator
from src.operators.redirect import TresorioRedirectRegisterOperator
from src.operators.delete_render import TresorioDeleteRenderOperator
from src.operators.redirect import TresorioRedirectGetCreditsOperator
from src.operators.redirect import TresorioRedirectDownloadAddon
from src.operators.redirect import TresorioRedirectForgotPasswordOperator
from src.operators.delete_all_renders import TresorioDeleteAllRendersOperator
from src.operators.download_render_results import TresorioDownloadRenderResultsOperator
from src.operators.async_loop import TresorioAsyncLoopModalOperator
from src.operators.logout import logout
from src.operators.async_loop import setup_asyncio_executor
from src.config.user_json import set_user_config

from src.config.api import API_CONFIG

bl_info = {
    'name': 'Tresorio cloud rendering',
    'version': (1, 0, 0),
    'blender': (2, 80, 0),
    'category': 'Output',
    'file': '/$HOME/.config/blender/2.80/scripts/addons/tresorio',
    'location': 'Properties: Output > Tresorio',
    'description': 'Cloud distributed rendering for Blender, by Tresorio',
    'wiki_url': 'https://tresorio.com/en/how-to-render-in-blender-using-tresorio-cloud/',
}

assert bl_info['version'] == (API_CONFIG['version']['major'], API_CONFIG['version']['minor'], API_CONFIG['version']['patch']), "Version in config.json must match the bl_info"

TO_REGISTER_CLASSES = (
    # Properties
    TresorioUserProps,
    TresorioReportProps,
    TresorioUserSettingsProps,
    TresorioRenderPacksProps,
    TresorioRenderFormProps,
    TresorioRendersDetailsProps,
    # Operators
    TresorioLoginOperator,
    TresorioLogoutOperator,
    TresorioRedirectForgotPasswordOperator,
    TresorioRedirectRegisterOperator,
    TresorioRedirectHomeOperator,
    TresorioUploadOperator,
    TresorioRenderFrameOperator,
    TresorioDownloadRenderResultsOperator,
    TresorioStopRenderOperator,
    TresorioDeleteRenderOperator,
    TresorioRedirectGetCreditsOperator,
    TresorioDeleteAllRendersOperator,
    TresorioAsyncLoopModalOperator,
    TresorioRedirectDownloadAddon,
    # UI
    TresorioMainPanel,
    TresorioRendersPanel,
    TresorioNewRenderPanel,
    TresorioAccountPanel,
    TresorioRendersList,
)


def unregister():
    """Unregister the addon from blender"""
    logout(bpy.context)

    set_user_config()
    atexit.unregister(set_user_config)
    atexit.unregister(TresorioIconsLoader.unregister)

    for cls in reversed(TO_REGISTER_CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError as exc:
            print(exc)
    TresorioIconsLoader.unregister()


def register():
    """Register the addon in blender"""
    atexit.register(set_user_config)
    atexit.register(TresorioIconsLoader.unregister)
    asyncio.get_event_loop().close()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    setup_asyncio_executor()

    TresorioIconsLoader.register()
    for cls in TO_REGISTER_CLASSES:
        bpy.utils.register_class(cls)


if __name__ == '__main__':
    register()
