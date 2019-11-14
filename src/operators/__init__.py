"""Entrypoint of the `operators` module"""

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

MODULES = (
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

for module in MODULES:
    reload(module)
