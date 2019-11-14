"""Entrypoint of the `services` module"""

from importlib import reload
from . import (
    backend,
    loggers,
    nas,
    platform,
)

MODULES = (
    backend,
    loggers,
    nas,
    platform,
)

for module in MODULES:
    reload(module)
