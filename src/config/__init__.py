from importlib import reload
from . import (
    api,
    debug,
    paths,
    enums,
    user_json,
    langs,
)

modules = (
    api,
    debug,
    paths,
    enums,
    langs,
    user_json,
)

for module in modules:
    reload(module)
