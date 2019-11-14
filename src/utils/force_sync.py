"""This module defines a function to convert an async function to sync"""

from functools import wraps
from typing import Any, Callable, Coroutine
import asyncio


def force_sync(func: Coroutine):
    """Modify an async function so it runs like a sync one"""
    @wraps(func)
    def sync(*args: Any,
             **kwargs: Any
             ) -> Callable[[Any], Any]:
        coro = func(*args, **kwargs)
        loop = asyncio.new_event_loop()
        res = loop.run_until_complete(coro)
        loop.close()
        return res
    return sync
