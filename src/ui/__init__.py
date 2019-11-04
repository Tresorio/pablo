from importlib import reload
from . import (
    icons,
    draw_connection_panel,
    main_panel,
    new_render_panel,
    draw_selected_render,
    user_renders_panel,
    account_panel,
    popup,
)

modules = (
    icons,
    draw_connection_panel,
    main_panel,
    new_render_panel,
    draw_selected_render,
    user_renders_panel,
    account_panel,
    popup,
)

for module in modules:
    reload(module)
