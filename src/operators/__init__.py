from importlib import reload
from . import (
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
