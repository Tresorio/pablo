from typing import Set
import os
import bpy
import sys
import subprocess
import threading
import queue

cancel_upload = False

def stop_upload_modal():
    global cancel_upload
    cancel_upload = True


end_callback = lambda exit_code : None
error_callback = lambda error: None


upload_start_callback = lambda target_path : None
upload_progress_callback = lambda filename, progress : None
upload_end_callback = lambda target_path, success : None
upload_error_callback = lambda filename, error : None


pack_start_callback = lambda blend_path, target_path : None
pack_progress_callback = lambda progress : None
missing_file_callback = lambda blend_path, target_path, file : None
pack_end_callback = lambda blend_path, target_path, success : None
pack_error_callback = lambda blend_path, target_path, error : None
project_creation_error_callback = lambda project_name, error : None


class TresorioUploadModalOperator(bpy.types.Operator):
    """Model operator running the asyncio loop"""
    bl_idname = 'tresorio.upload_modal'
    bl_label = 'Runs the asyncio main loop'
    bl_options = {'INTERNAL'}
    timer = None
    stop = False

    blend_path: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    target_path: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    project_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    url: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    cookie: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    storage_url: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    storage_access_key: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    storage_secret_key: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})
    bucket_name: bpy.props.StringProperty(options={'HIDDEN', 'SKIP_SAVE'})



    def execute(self,
                context: bpy.types.Context
                ) -> Set[str]:
        """When calling bpy.ops.tresorio.loop"""
        global cancel_upload
        cancel_upload = False

        script_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'services', 'uploader.py'))
        self.cmd = [sys.argv[0], '--factory-startup', '-noaudio', '-b', '-P', script_path, '--', self.blend_path, self.target_path, self.project_name, self.url, self.cookie, self.storage_url, self.storage_access_key, self.storage_secret_key, self.bucket_name]
        self.stop = False

        return self.invoke(context, None)


    def invoke(self,
               context: bpy.types.Context,
               event
               ) -> Set[str]:
        """Called when invoking the operator"""
        del event

        print('Launching uploading subprocess')
        self.process = subprocess.Popen(
            self.cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT,
            bufsize = 0
        )

        self.safe_queue = queue.Queue()

        thread = threading.Thread(target = self.watch_process, args = ())
        thread.daemon = True
        thread.start()

        context.window_manager.modal_handler_add(self)

        winman = context.window_manager
        self.timer = winman.event_timer_add(0.01, window=context.window)

        return {'RUNNING_MODAL'}


    def modal(self,
              context: bpy.types.Context,
              event
              ) -> Set[str]:
        """Modal running of the operator"""
        if event.type != 'TIMER':
            return {'PASS_THROUGH'}

        if cancel_upload:
            self.process.kill()
        if self.stop and self.safe_queue.empty():
            context.window_manager.event_timer_remove(self.timer)
            return {'FINISHED'}

        try:
            log = self.safe_queue.get_nowait()
        except queue.Empty: pass
        else:
            if log.startswith('CALLBACK'):
                self.__callback(log.lstrip('CALLBACK').strip())
            else:
                print('Upload subprocess |', log.rstrip())

        return {'RUNNING_MODAL'}


    def watch_process(self):
        try:
            while True:
                exit_code = self.process.poll()
                log = self.process.stdout.readline().decode('UTF-8')
                if not log and exit_code is not None:
                    break
                if log and log != '':
                    self.safe_queue.put(log)
            print('Uploading subprocess finished - exited with code', exit_code)
        except Exception as error:
            self.safe_queue.put(f'CALLBACK ERROR {str(error)}')
        finally:
            self.safe_queue.put(f'CALLBACK END {str(exit_code if exit_code is not None else 1)}')
            self.stop = True


    def __callback(self, string: str):
        if string.startswith('ERROR'):
            _, error = string.split(' ', 1)
            error_callback(error)
        elif string.startswith('END'):
            _, exit_code = string.split()
            end_callback(int(exit_code))
        elif string.startswith('UPLOAD_START'):
            _, target_path = string.split()
            upload_start_callback(target_path)
        elif string.startswith('UPLOAD_PROGRESS'):
            _, filename, progress = string.split()
            upload_progress_callback(filename, float(progress))
        elif string.startswith('UPLOAD_END'):
            _, target_path, success = string.split()
            upload_end_callback(target_path, success == 'True')
        elif string.startswith('UPLOAD_ERROR'):
            _, filename, error = string.split(' ', 2)
            upload_error_callback(filename, error)
        elif string.startswith('PACK_START'):
            _, blend_path, target_path = string.split()
            pack_start_callback(blend_path, target_path)
        elif string.startswith('PACK_PROGRESS'):
            _, progress = string.split()
            pack_progress_callback(float(progress))
        elif string.startswith('MISSING_FILE'):
            _, blend_path, target_path, file = string.split(' ', 3)
            missing_file_callback(blend_path, target_path, file)
        elif string.startswith('PACK_END'):
            _, blend_path, target_path, success = string.split()
            pack_end_callback(blend_path, target_path, success == 'True')
        elif string.startswith('PACK_ERROR'):
            _, blend_path, target_path, error = string.split(' ', 3)
            pack_error_callback(blend_path, target_path, error)
        elif string.startswith('PROJECT_CREATION_ERROR'):
            _, project_name, error = string.split(' ', 2)
            project_creation_error_callback(project_name, error)
        else:
            print(f'Unknown callback: {string}')
