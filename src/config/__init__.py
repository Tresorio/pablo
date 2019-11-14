"""Entrypoint of the `config` module"""

from importlib import reload
from . import (
    api,
    debug,
    paths,
    enums,
    user_json,
    langs,
)

MODULES = (
    api,
    debug,
    paths,
    enums,
    langs,
    user_json,
)

for module in MODULES:
    reload(module)
