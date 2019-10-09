from importlib import reload
from . import (
    email,
    json_rw,
    lockfile,
    password,
    percent_reader,
)

modules = (
    email,
    json_rw,
    lockfile,
    password,
    percent_reader,
)

for module in modules:
    reload(module)