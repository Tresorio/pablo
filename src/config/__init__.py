from importlib import reload
from . import (
    api,
    debug,
    langs,
    paths,
)

modules = (
    api,
    debug,
    langs,
    paths,
)

for module in modules:
    reload(module)
