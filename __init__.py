import os
import sys
import bpy

sys.path.append("/home/robin/Tresorio/pablo") ## locate submodules TODO remove it, it's temporary
user_path = bpy.utils.resource_path('USER')
config_path = os.path.join(user_path, "config")
addon_path = os.path.join(config_path, "pablo")
sys.path.append(addon_path)

from src.login.logout_op import TresorioLogout
from src.login.login_op import TresorioLogin
from src.settings.property import TresorioSettings
from src.main_panel.panel import TresorioPanel

bl_info = {
    "name": "Tresorio cloud rendering",
    "version": (0, 0, 0),
    "blender": (2, 80, 0),
    "file": "/home/$USER/.config/blender/2.80/scripts/addons/pablo",
    "location": "Render > Tresorio Rendering",
    "description": "Cloud distributed rendering for Blender",
    "warning": "",
}


classes = (TresorioSettings,
           TresorioLogin,
           TresorioLogout,
           TresorioPanel)

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
    for cls in classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
