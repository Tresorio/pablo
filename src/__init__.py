"""Entrypoint of the `src` module"""

from importlib import reload
from . import (
    utils,
    config,
    properties,
    operators,
    services,
    ui,
)

MODULES = (
    utils,
    config,
    properties,
    operators,
    services,
    ui,
)

for module in MODULES:
    reload(module)
