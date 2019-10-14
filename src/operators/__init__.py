from importlib import reload
from . import (
    delete_render,
    download_render_results,
    login,
    logout,
    redirect,
    render,
    stop_render,
    popup,
)

modules = (
    delete_render,
    download_render_results,
    login,
    logout,
    redirect,
    render,
    stop_render,
    popup,
)

for module in modules:
    reload(module)
