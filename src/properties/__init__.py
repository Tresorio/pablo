from importlib import reload
from . import (
    render_form,
    render_packs,
    renders,
    report_props,
    user_props,
)

if 'src.properties' in locals():
    modules = (
        render_form,
        render_packs,
        renders,
        report_props,
        user_props,
    )

    for module in modules:
        reload(module)
