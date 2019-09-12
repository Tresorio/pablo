#!/usr/bin/env python3

import io
import os
import asyncio
import aiohttp

from nas import Nas


async def upload(filepath: str):
    with AioPercentUpload(filepath) as f:
        async with Nas('http://0.0.0.0:7777') as nas:
            return await nas.upload_content('test', f, 'myfile.txt', read=False)

class AioPercentUpload(io.BufferedReader):
    def __init__(self, file_path, pointer=None):
        super().__init__(open(file_path, "rb"))
        self.percent = 0.0
        self.total = os.path.getsize(file_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def read(self, *args, **kwargs):
        chunk = super().read(*args, **kwargs)
        self.percent += len(chunk) / self.total * 100
        print(f'\r{self.percent:.2f}%', end='', flush=True)
        return chunk

    def close(self):
        super().close()


task = upload(
    '/home/robin/Downloads/blender-2.79b-linux-glibc219-x86_64.tar.bz2')
print(asyncio.run(task))
