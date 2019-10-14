import bpy


def popup(msg: str = '', title: str = '', icon: str = 'NONE', icon_value: int = 0):
    def draw(wm, context): return wm.layout.label(
        text=msg, icon=icon, icon_value=icon_value)
    bpy.context.window_manager.popup_menu(
        draw, title=title)
