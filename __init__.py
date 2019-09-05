bl_info = {
    "name": "Tresorio cloud rendering",
    "version": (0, 0, 0),
    "blender": (2, 80, 0),
    "category": "Render",
    "file": "/$HOME/.config/blender/2.80/scripts/addons/tresorio_rendering",
    "location": "Properties: Render > Tresorio Rendering",
    "description": "Cloud distributed rendering for Blender, by Tresorio",
    "wiki_url": "http://192.168.15.20:3000",
}

def is_connected():
    import socket
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

def reload_all():
    """Reloads recursively all the modules"""
    __all__ = []
    for loader, module_name, _ in pkgutil.walk_packages(__path__):
        __all__.append(module_name)
        _module = loader.find_module(module_name).load_module(module_name)
        globals()[module_name] = _module


if "bpy" in locals():
    import pkgutil
    reload_all()
    del pkgutil
else:
    import os
    import sys
    import bpy
    # locate submodules TODO remove it, it's temporary, for dev (symlink)
    sys.path.append("/home/robin/Tresorio/pablo")
    user_path = bpy.utils.resource_path('USER')
    addon_path = os.path.join(user_path, "config", "pablo")
    sys.path.append(addon_path)


import src
from src.settings.property import TresorioSettings
from src.login.logout_op import TresorioLogout
from src.login.login_op import TresorioLogin
from src.main_panel.panel import TresorioPanel
from src.main_panel.redirect import TresorioRedirectForgotPassword, TresorioRedirectRegister
from src.render.frame_op import TresorioRenderFrame

classes = (TresorioSettings,
           TresorioLogin,
           TresorioLogout,
           TresorioPanel,
           TresorioRedirectForgotPassword,
           TresorioRedirectRegister,
           TresorioRenderFrame)

def make_annotations(cls):
    """Converts class fields to annotations if running with Blender 2.8"""
    if bpy.app.version < (2, 80):
        return cls
    bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


def register():
    if is_connected() == True:
        for cls in classes:
            ## The 2.80 way hotfix, TODO change the settings properties to be compliant
            make_annotations(cls)
            ## Add description with language translation
            set_doc = getattr(cls, "set_doc", None)
            if callable(set_doc):
                cls.set_doc()
            bpy.utils.register_class(cls)
    else:
        print("NO CONNECTION")
        ## TODO show a reload panel once connected


def unregister():
    for cls in classes:
        if cls.__doc__ != "":
            bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
