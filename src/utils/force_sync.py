import asyncio
from functools import wraps


def force_sync(func):
    @wraps(func)
    def sync(*args, **kwargs):
        coro = func(*args, **kwargs)
        loop = asyncio.new_event_loop()
        res = loop.run_until_complete(coro)
        loop.close()
        return res
    return sync
