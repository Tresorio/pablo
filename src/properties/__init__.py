"""Entrypoint of the `properties` module"""

from importlib import reload
from . import (
    render_form,
    render_packs,
    renders,
    report_props,
    user_props,
    user_settings,
)

MODULES = (
    render_form,
    render_packs,
    renders,
    report_props,
    user_props,
    user_settings,
)

for module in MODULES:
    reload(module)
