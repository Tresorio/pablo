# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

"""Manages the asyncio loop."""

import asyncio
import traceback
import concurrent.futures
import logging
import gc
import typing

import bpy

# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
_loop_kicking_operator_running = False


def setup_asyncio_executor():
    """Sets up AsyncIO to run properly on each platform."""
    import sys

    if sys.platform == 'win32':
        loop = asyncio.get_event_loop()
        if loop.is_closed is False:
            asyncio.get_event_loop().close()
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    loop.set_default_executor(executor)
    loop.set_debug(False)


def kick_async_loop(*args) -> bool:
    """Performs a single iteration of the asyncio event loop.

    :return: whether the asyncio loop should stop after this kick.
    """

    loop = asyncio.get_event_loop()
    stop_after_this_kick = False

    if loop.is_closed():
        return True

    all_tasks = asyncio.Task.all_tasks()
    if not len(all_tasks):
        stop_after_this_kick = True

    elif all(task.done() for task in all_tasks):
        log.debug('all %i tasks are done, fetching results and stopping after this kick.',
                  len(all_tasks))
        stop_after_this_kick = True

        # Clean up circular references between tasks.
        gc.collect()

        for task_idx, task in enumerate(all_tasks):
            if not task.done():
                continue
            try:
                res = task.result()
                log.debug('   task #%i: result=%r', task_idx, res)
            except asyncio.CancelledError:
                log.debug('   task #%i: cancelled', task_idx)
            except Exception:
                print('{}: resulted in exception'.format(task))
                traceback.print_exc()
    loop.stop()
    loop.run_forever()
    return stop_after_this_kick


def ensure_async_loop():
    bpy.ops.asyncio.loop()


def erase_async_loop():
    global _loop_kicking_operator_running
    loop = asyncio.get_event_loop()
    loop.stop()


class AsyncLoopModalOperator(bpy.types.Operator):
    bl_idname = 'asyncio.loop'
    bl_label = 'Runs the asyncio main loop'
    bl_options = {'INTERNAL'}
    timer = None

    def __del__(self):
        global _loop_kicking_operator_running
        _loop_kicking_operator_running = False

    def execute(self, context):
        return self.invoke(context, None)

    def invoke(self, context, event):
        global _loop_kicking_operator_running

        if _loop_kicking_operator_running:
            return {'PASS_THROUGH'}

        context.window_manager.modal_handler_add(self)
        _loop_kicking_operator_running = True

        wm = context.window_manager
        self.timer = wm.event_timer_add(0.000001, window=context.window)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global _loop_kicking_operator_running

        if not _loop_kicking_operator_running:
            return {'FINISHED'}

        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        stop_after_this_kick = kick_async_loop()
        if stop_after_this_kick:
            context.window_manager.event_timer_remove(self.timer)
            _loop_kicking_operator_running = False
            return {'FINISHED'}

        return {'RUNNING_MODAL'}


def shutdown_loop():
    tasks = asyncio.Task.all_tasks()
    for task in tasks:
        task.cancel()
    kick_async_loop() # kick the loop so the cancel takes effect
    erase_async_loop()
