"""Entrypoint of the `ui` module"""

from importlib import reload
from . import (
    draw_connection_panel,
    main_panel,
    new_render_panel,
    draw_selected_render,
    user_renders_panel,
    account_panel,
    popup,
)

MODULES = (
    # icons,
    draw_connection_panel,
    main_panel,
    new_render_panel,
    draw_selected_render,
    user_renders_panel,
    account_panel,
    popup,
)

for module in MODULES:
    reload(module)
