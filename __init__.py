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

import sys
import os
import bpy
from importlib import reload

user_path = bpy.utils.resource_path('USER')
addon_path = os.path.join(user_path, 'scripts', 'addons', 'pablo')
sys.path.append(addon_path)

from types import ModuleType

def reload_all(module: ModuleType, layers: int):
    """ TODO: remove this ugly trick and find a correct way to reload submodules"""
    if layers == 0: return
    for key in module.__dict__:
        attr = module.__dict__[key]
        if type(attr) is not ModuleType:
            continue
        reload_all(attr, layers - 1)
        reload(attr)

if 'bpy' in locals():
    import src
    reload_all(src, 2)

from src.properties import TresorioUserProps
from src.operators.logout import TresorioLogout
from src.operators.login import TresorioLogin
from src.operators.panel import TresorioPanel
from src.operators.redirect import TresorioRedirectForgotPassword, TresorioRedirectRegister
from src.operators.render import TresorioRenderFrame
from src.services.async_loop import AsyncLoopModalOperator

to_register_classes = (TresorioUserProps,
                       TresorioLogin,
                       TresorioLogout,
                       TresorioPanel,
                       TresorioRedirectForgotPassword,
                       TresorioRedirectRegister,
                       TresorioRenderFrame,
                       AsyncLoopModalOperator)


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
