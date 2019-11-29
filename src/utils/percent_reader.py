"""Defines a file reader that updates the percentage read."""
from queue import Queue
from typing import Any
import io
import os
import time

import bpy
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

    def __init__(self,
                 filepath: str,
                 update_queue: Queue = None
                 ):
        super().__init__(open(filepath, 'rb'))
        self.update_queue = update_queue
        self.percent = 0.0
        self.old_time = time.time()
        self.time = 0.0
        self.total = os.path.getsize(filepath)

    def __enter__(self):
        """Entrypoint of `with`."""
        return self

    def __exit__(self,
                 *args: Any):
        """Exit point of `with`."""
        if self.update_queue is not None:
            self.update_queue.put(('finished_upload', None))
        del args
        self.close()

    def read(self,
             *args: Any,
             **kwargs: Any
             ) -> bytes:
        """Returns a chunk of read bytes and updates advancement percent."""
        del kwargs
        chunk = super().read(*args)
        self.percent += len(chunk) / self.total * 100
        self.time = time.time()
        if self.time - self.old_time > 0.2:
            self.old_time = self.time
            self.time = 0.0
            if self.update_queue is not None:
                self.update_queue.put(('upload_percent', self.percent))
        return chunk
