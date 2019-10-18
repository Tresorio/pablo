from importlib import reload
from . import (
    async_loop,
    backend,
    loggers,
    nas,
    platform,
)

if 'src.services' in locals():
    modules = (
        async_loop,
        backend,
        loggers,
        nas,
        platform,
    )

    for module in modules:
        reload(module)
