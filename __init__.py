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
from src.properties.farm import TresorioFarmProps
from src.properties.user_settings import TresorioUserSettingsProps
from src.ui.main_panel import TresorioMainPanel
from src.ui.account_panel import TresorioAccountPanel
from src.ui.new_render_panel import TresorioNewRenderPanel
from src.ui.user_renders_panel import TresorioRendersPanel, TresorioRendersList
from src.ui.render_launch import TresorioRenderLauncher, TresorioRenderResumer, TresorioFarmList
from src.operators.popup import ErrorPopup, InfoPopup
from src.operators.login import TresorioLoginOperator
from src.operators.logout import TresorioLogoutOperator
from src.operators.resume_render import TresorioResumeRenderOperator
from src.operators.upload import TresorioUploadOperator
from src.operators.cancel_upload import TresorioCancelUploadOperator
from src.operators.gpu_render import TresorioGpuRenderFrameOperator
from src.operators.cpu_render import TresorioCpuRenderFrameOperator
from src.operators.cancel_rendering import TresorioCancelRenderingOperator
from src.operators.launch_rendering import TresorioLaunchRenderingOperator
from src.operators.launch_resume import TresorioLaunchResumeOperator
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
from src.operators.upload_modal import TresorioUploadModalOperator
from src.operators.logout import logout
from src.operators.async_loop import setup_asyncio_executor
from src.operators.advanced_settings import TresorioAdvancedSettingsNavigationOutOperator,\
    TresorioAdvancedSettingsNavigationInOperator,\
    TresorioAdvancedSettingsResetOperator,\
    TresorioAdvancedSettingsOperator
from src.config.user_json import set_user_config

from src.config.api import API_CONFIG

bl_info = {
    'name': 'Tresorio cloud rendering',
    'version': (2, 4, 0),
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
    TresorioFarmProps,
    TresorioRenderFormProps,
    TresorioRendersDetailsProps,
    # Operators
    TresorioLoginOperator,
    TresorioLogoutOperator,
    TresorioRedirectForgotPasswordOperator,
    TresorioRedirectRegisterOperator,
    TresorioRedirectHomeOperator,
    TresorioUploadOperator,
    TresorioCancelUploadOperator,
    ErrorPopup,
    InfoPopup,
    TresorioGpuRenderFrameOperator,
    TresorioCpuRenderFrameOperator,
    TresorioLaunchResumeOperator,
    TresorioCancelRenderingOperator,
    TresorioDownloadRenderResultsOperator,
    TresorioStopRenderOperator,
    TresorioDeleteRenderOperator,
    TresorioRedirectGetCreditsOperator,
    TresorioDeleteAllRendersOperator,
    TresorioAsyncLoopModalOperator,
    TresorioUploadModalOperator,
    TresorioRedirectDownloadAddon,
    TresorioResumeRenderOperator,
    TresorioAdvancedSettingsNavigationInOperator,
    TresorioAdvancedSettingsNavigationOutOperator,
    TresorioAdvancedSettingsOperator,
    TresorioAdvancedSettingsResetOperator,
    TresorioLaunchRenderingOperator,
    # UI
    TresorioMainPanel,
    TresorioRendersPanel,
    TresorioNewRenderPanel,
    TresorioAccountPanel,
    TresorioRendersList,
    TresorioFarmList,
    TresorioRenderLauncher,
    TresorioRenderResumer
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
