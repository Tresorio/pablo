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

def reload_all():
    """Reloads recursively all the modules"""
    __all__ = []
    for loader, module_name, _ in pkgutil.walk_packages(__path__):
        print(f'reloading: {module_name}')
        __all__.append(module_name)
        _module = loader.find_module(module_name).load_module(module_name)
        globals()[module_name] = _module


if 'bpy' in locals():
    import pkgutil
    reload_all()
    del pkgutil
else:
    import os
    import sys
    import bpy
    # locate submodules TODO remove it, it's temporary, for dev (symlink)
    sys.path.append('/home/robin/Tresorio/pablo')
    user_path = bpy.utils.resource_path('USER')
    addon_path = os.path.join(user_path, 'config', 'pablo')
    sys.path.append(addon_path)


import src
from src.properties.property import TresorioSettings
from src.operators.logout import TresorioLogout
from src.operators.login import TresorioLogin
from src.operators.panel import TresorioPanel
from src.operators.redirect import TresorioRedirectForgotPassword, TresorioRedirectRegister
from src.operators.render import TresorioRenderFrame
from src.async_loop import AsyncLoopModalOperator

classes = (TresorioSettings,
           TresorioLogin,
           TresorioLogout,
           TresorioPanel,
           TresorioRedirectForgotPassword,
           TresorioRedirectRegister,
           TresorioRenderFrame,
           AsyncLoopModalOperator)


def register():
    for cls in classes:
        ## Add description with language translation
        set_doc = getattr(cls, 'set_doc', None)
        if callable(set_doc):
            cls.set_doc()
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
