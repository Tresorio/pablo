from importlib import reload
from . import (
    icons,
    draw_connection_panel,
    main_panel,
    new_render_panel,
    selected_render_panel,
    user_renders_panel,
    account_panel,
    popup,
)

if 'src.ui' in locals():
    modules = (
        icons,
        draw_connection_panel,
        main_panel,
        new_render_panel,
        selected_render_panel,
        user_renders_panel,
        account_panel,
        popup,
    )

    for module in modules:
        reload(module)
