"""This module defines utilities to show popups in blender"""

import bpy

def popup(msg: str = '',
          title: str = '',
          icon: str = 'NONE',
          icon_value: int = 0
          ) -> None:
    """Show a popup in the blender's window manager

    Args:
        msg (optional): The main body of the popup
        title (optional): Title wrote on top of the popup
        icon (optional): One of the Blender default icon
        icon_value (optional): Same as icon but for custom icons
    """
    def draw(window_manager: bpy.types.WindowManager,
             context: bpy.types.Context
             ) -> None:
        """Draw the popup layout"""
        del context
        window_manager.layout.label(text=msg, icon=icon, icon_value=icon_value)

    bpy.context.window_manager.popup_menu(draw, title=title)

def alert(msg: str = '', subtitle: str = '') -> None:
    bpy.ops.object.error_popup('INVOKE_DEFAULT', error_msg=msg, subtitle=subtitle)

def notif(msg: str = '') -> None:
    bpy.ops.object.info_popup('INVOKE_DEFAULT', info_msg=msg)