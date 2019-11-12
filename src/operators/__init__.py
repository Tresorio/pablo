from importlib import reload
from . import (
    delete_all_renders,
    download_render_results,
    login,
    logout,
    redirect,
    render,
    stop_render,
    popup,
    delete_render,
)

modules = (
    delete_all_renders,
    download_render_results,
    login,
    logout,
    redirect,
    render,
    stop_render,
    popup,
    delete_render,
)

for module in modules:
    reload(module)
