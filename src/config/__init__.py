from importlib import reload
from . import (
    api,
    debug,
    langs,
    paths,
    enums,
)

modules = (
    api,
    debug,
    langs,
    paths,
    enums,
)

for module in modules:
    reload(module)
