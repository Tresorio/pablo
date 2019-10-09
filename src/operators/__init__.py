from importlib import reload
from . import (
    delete_render,
    download_render_results,
    login,
    logout,
    redirect,
    render,
    stop_render,
)

modules = (
    delete_render,
    download_render_results,
    login,
    logout,
    redirect,
    render,
    stop_render,
)

for module in modules:
    reload(module)
