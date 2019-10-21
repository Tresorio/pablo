import asyncio
import functools

def force_sync(fn):
    """Convert async function to sync"""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        res = fn(*args, **kwargs)
        if asyncio.iscoroutine(res):
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(res)
        return res
    return wrapper