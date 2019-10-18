from importlib import reload
from . import (
    json_rw,
    lockfile,
    password,
    percent_reader,
)

if 'src.utils' in locals():
    modules = (
        json_rw,
        lockfile,
        password,
        percent_reader,
    )

    for module in modules:
        reload(module)
