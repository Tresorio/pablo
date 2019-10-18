from importlib import reload
from . import (
    utils,
    config,
    properties,
    operators,
    services,
    ui,
)

if 'src' in locals():
    modules = (
        operators,
        ui,
        utils,
        services,
        properties,
        config,
    )

    for module in modules:
        reload(module)
