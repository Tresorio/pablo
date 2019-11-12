"""Defines a file reader that updates the percentage read."""
import io
import os
import bpy
import time


from types import FunctionType
from functools import wraps


class PercentReader(io.BufferedReader):
    """Computes the percent read of a file.

    Args:
        file_path: file to read.

    Example:

        >>> with PercentReader('./my_file.txt') as file:
        ...     async with aiohttp.ClientSession() as session:
        ...         data = {'file': file}
        ...         res = await session.post('http://0.0.0.0:3000', data = data)
    """

    def __init__(self, filepath: str, update: FunctionType):
        bpy.context.scene.tresorio_render_form.upload_percent = 0.0
        super().__init__(open(filepath, "rb"))
        self.update = update
        self.filepath = filepath
        self.percent = 0.0
        self.old_time = time.time()
        self.time = 0.0
        self.total = os.path.getsize(filepath)

    def __enter__(self):
        """Entrypoint of `with`."""
        return self

    def __exit__(self, *args):
        """Exit point of `with`."""
        del args
        self.close()

    def read(self, *args, **kwargs):
        """Returns a chunk of read bytes and updates advancement percent."""
        chunk = super().read(*args)
        self.percent += len(chunk) / self.total * 100
        self.time = time.time()
        if self.time - self.old_time > 0.25:
            self.old_time = self.time
            self.time = 0.0
            self.update(self.percent)
        return chunk
