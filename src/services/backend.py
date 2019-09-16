import os
import bpy
import asyncio
from . import async_loop
from .nas import Nas
from src.utils.percent_reader import PercentReader
from dataclasses import dataclass

@dataclass
class Render:
    """Description of the render to realize.""" 
    filepath: str
    rendering_name: str

class Renderer:

    def __init__(self):
        pass

    async def get_upload_nas(self):
        pass

    async def upload_blend_file(self, req: Render):
        # TODO: query Gandalf to get Nassim token and uuid
        # nas_task = asyncio.ensure_future(self.get_upload_nas())
        ## nas_task.add_done_callback(any_sync_func_ptr)
        # nas_spec = async_loop.ensure_async_loop()
        blendfile_name = os.path.basename(req.filepath)
        async with Nas('http://0.0.0.0:7777') as nas:
            with PercentReader(req.filepath, verbose=1) as file:
                res = await nas.upload_content('test', file, blendfile_name)
        return res
