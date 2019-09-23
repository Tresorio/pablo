bl_info = {
    'name': 'WIP Tresorio cloud rendering',
    'version': (0, 0, 0),
    'blender': (2, 80, 0),
    'category': 'Render',
    'file': '/$HOME/.config/blender/2.80/scripts/addons/tresorio_rendering',
    'location': 'Properties: Render > Tresorio Rendering',
    'description': 'Cloud distributed rendering for Blender, by Tresorio',
    'wiki_url': 'http://192.168.15.20:3000',
}

import os

try:
    import aiohttp
    del aiohttp
except ModuleNotFoundError:
    os.system('pip install --user aiohttp')

import sys
import bpy
from importlib import reload
from types import ModuleType

user_path = bpy.utils.resource_path('USER')
addon_path = os.path.join(user_path, 'scripts', 'addons', 'pablo')
sys.path.append(addon_path)

def reload_all(module: ModuleType, layers: int):
    if layers == 0: return
    for key in module.__dict__:
        if key == 'bpy':
            continue
        attr = module.__dict__[key]
        if type(attr) is not ModuleType:
            continue
        reload_all(attr, layers - 1)
        reload(attr)

if 'bpy' in locals():
    import src
    reload_all(src, 2)

from src.properties.user_props import TresorioUserProps
from src.properties.report_props import TresorioReportProps
from src.properties.render_form import TresorioRenderFormProps
from src.properties.render_packs import TresorioRenderPacksProps

from src.ui.main_panel import TresorioMainPanel
from src.ui.account_panel import TresorioAccountPanel
from src.ui.new_render_panel import TresorioNewRenderPanel

from src.operators.login import TresorioLoginOperator
from src.operators.logout import TresorioLogoutOperator
from src.operators.render import TresorioRenderFrameOperator
from src.operators.redirect import TresorioRedirectHomeOperator
from src.operators.redirect import TresorioRedirectRegisterOperator
from src.operators.redirect import TresorioRedirectForgotPasswordOperator
from src.services.async_loop import AsyncLoopModalOperator

to_register_classes = (
                       # Properties 
                       TresorioUserProps,
                       TresorioReportProps,
                       TresorioRenderPacksProps,
                       TresorioRenderFormProps,

                       # Operators
                       TresorioLoginOperator,
                       TresorioLogoutOperator,
                       TresorioRedirectForgotPasswordOperator,
                       TresorioRedirectRegisterOperator,
                       TresorioRedirectHomeOperator,
                       TresorioRenderFrameOperator,
                       AsyncLoopModalOperator,

                       # UI
                       TresorioMainPanel,
                       TresorioNewRenderPanel,
                       TresorioAccountPanel,
                      )


def unregister():
    for cls in reversed(to_register_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError as exc:
            print(exc)
            return


def register():
    for cls in to_register_classes:
        ## Add description with language translation
        set_doc = getattr(cls, 'set_doc', None)
        if callable(set_doc):
            cls.set_doc()
        bpy.utils.register_class(cls)


if __name__ == '__main__':
    register()
