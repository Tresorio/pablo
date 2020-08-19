import multiprocessing
import multiprocessing.pool
import pathlib
import os
import math
import requests
import zlib
import subprocess
import threading
import sys
from urllib.parse import urljoin
from http import HTTPStatus
from typing import Callable, Any, Union, Tuple, Dict


# Allow blender_asset_tracer to be imported in addon-mode as module AND as a standalone script when launched in subprocess
import site
site.addsitedir(os.path.dirname(os.path.abspath(__file__)))
from blender_asset_tracer import bpathlib, pack


class Platform:
    '''Tresorio's backend sdk

    Example:
        >>> async with Platform() as plt:
        ...     credentials = {
        ...         'email': 'tresorio@demo.com',
        ...         'password': 'tresorio'
        ...     }
        ...     res = await plt.req_connect_to_tresorio(credentials)

    '''

    def __init__(self, base_url):
        self.url = base_url
        self.session = None


    def __enter__(self):
        '''Entrypoint of `with` to init the platform sdk'''
        return self

    def __exit__(self, *args: Any):
        '''Exitpoint of the `with` block to close the platform sdk'''
        if self.session is not None:
            self.session.close()

    @staticmethod
    def _platformrequest(func: Callable[[str, Any], requests.Response]):
        '''Wrapper used to skip code duplication over the Nas's methods.

        It will create a new requests client session if there wasn't any before
        (happens when Platform is instanciated outside of `with`).

        Arg:
            func: Platform's method to decorate.

        Returns:
            The newly decorated function.

        Example:
            As _platformrequest is a @staticmethod, we need to access its function
            with __func__.

            >>> @_platformrequest.__func__
            ... def platform_method(self, *arg):
            ...     pass
        '''
        def wrapper(self, *args: Any, read: bool = False, jsonify: bool = False, **kwargs: Any) -> Union[bytes, Dict[str, Any], requests.Response]:
            '''This wrapper handles common cases of platform requests

            Args:
                read: If `False`, the wrapped function will return the whole
                response. If `True`, will read the response and return bytes
                jsonify (overides `read`): If `False`, will proceed the `read` arg.
                Else, will return the body as a dict.
            '''
            if self.session is None:
                self.session = requests.sessions.Session()
            res = func(self, *args, **kwargs)
            res.raise_for_status()
            if jsonify is True:
                return res.json()
            if read is True:
                return res.content
            return res
        return wrapper


    @_platformrequest.__func__
    def get_nas(self, token: str, size: int, project_name: str) -> requests.Response:
        """Get a server to upload project

        Args:
            token: The token given at the connection to Tresorio's API.

        Example:
            >>> with Platform() as plt:
            ...     size = 42
            ...     token = 'eyJ0eXAiOiJKV1QiLC'
            ...     project_name = 'Untitled'
            ...     res = await plt.get_nas(token, size, project_name)
        """
        headers = {
            'Authorization': f'JWT {token}',
            'Content-Type': 'application/json'
        }
        data = {'size': size, 'name': project_name}
        url = urljoin(self.url, '/user/products/render/scene')
        return self.session.post(url, headers=headers, json=data, verify=True)


    def close(self):
        '''Close the aiohttp session. To use if Nas is not instanciated with `with`.'''
        if self.session is not None:
            self.session.close()


class Nas:
    '''Tresorio's Nas synchronous sdk. It is bundled in this file to let it be executed as a standalone script

    Args:
        base_url (str): The url of the Nas with which to interact.

    Examples:
        This example shows the way to setup a Nas instance that will
        interact with the Nas API:

        >>> nas = Nas('http://0.0.0.0:3000')

        The __enter__ and __exit__ allow the use of with:

        >>> with Nas('http://0.0.0.0:3000') as nas:
        ...     nas.download('uuid', 'file.txt')

    '''


    def __init__(self, base_url: str):
        self.url = base_url
        self.session = None


    def __enter__(self):
        '''Entrypoint of `with`'''
        return self

    def __exit__(self, *args: Any):
        '''Callback once out of the `with` block'''
        if self.session is not None:
            self.session.close()

    @staticmethod
    def _nasrequest(func: Callable[[Any], requests.Response]):
        '''Wrapper used to skip code duplication over the Nas's methods.

        It will create a new requests client session if there wasn't any before
        (happens when Nas is instanciated outside of `with`).

        Args:
            func: Nas's method to decorate.args

        Returns:
            The newly decorated function.

        Example:
            As _nasrequest is a @staticmethod, we need to access its function
            with __func__.

            >>> @_nasrequest.__func__
            ... def Nas_method(self, uuid):
            ...     pass
        '''

        def wrapper(self, *args: Any, read: bool = False, **kwargs: Any) -> Union[requests.Response, bytes, None]:
            '''This wrapper handles common cases of nas requests

            Arg:
                read: If `False`, the wrapped function will return the whole
                    response. If `True`, will read the response and return bytes
            '''
            if self.session is None:
                self.session = requests.sessions.Session()
            res = func(self, *args, **kwargs)
            res.raise_for_status()
            if read is True:
                return res.content
            return res
        return wrapper


    @_nasrequest.__func__
    def upload_chunk(self, jwt: str, headers: str, data) -> requests.Response:
        headers['Authorization'] = f'JWT {jwt}'
        url = urljoin(self.url, '/chunk')
        return self.session.post(url, headers=headers, data=data, verify=True)


    @_nasrequest.__func__
    def check_file(self, jwt: str, headers: str) -> requests.Response:
        headers['Authorization'] = f'JWT {jwt}'
        url = urljoin(self.url, '/chunk')
        return self.session.get(url, headers=headers, verify=True)


    @_nasrequest.__func__
    def merge_file(self, jwt: str, headers: str) -> requests.Response:
        headers['Authorization'] = f'JWT {jwt}'
        url = urljoin(self.url, '/chunkend')
        return self.session.get(url, headers=headers, verify=True)


    def close(self):
        '''Close the aiohttp session. To use if Nas is not instanciated with `with`.'''
        if self.session is not None:
            self.session.close()


class UploadJob:


    def __init__(self, path: str, root: str, chunk_size: int):
        self.path = path
        relpath = pathlib.Path(os.path.relpath(path, root))
        self.upload_path = str(pathlib.PurePosixPath(relpath))

        self.retries = 0
        self.uploaded_chunks = 0
        self.chunk_size = chunk_size
        self.size = os.stat(path).st_size
        self.number_of_chunks = math.ceil(self.size / chunk_size)
        self.file_checksum = self.__file_crc32(path)

        print(f'Created job for \'{relpath}\' ({self.size} bytes, {self.number_of_chunks} chunks)')
        sys.stdout.flush()


    def __file_crc32(self, path: str, chunk_size: int = 65536):
        with open(path, 'rb') as file:
            checksum = 0
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                checksum = zlib.crc32(chunk, checksum)
            return str(checksum)


class Uploader:
    jobs: [UploadJob] = []
    stop = False


    def __init__(
        self,
        blend_path: str,
        target_path: str,
        project_name: str,
        url: str,
        jwt: str,
        chunk_size: int = 16 * 1024 * 1024,
        max_retries_per_chunk: int = 5,
        number_of_threads: int = 3,
    ):
        self.chunk_size = chunk_size
        self.max_retries_per_chunk = max_retries_per_chunk
        self.number_of_threads = number_of_threads
        self.url = url
        self.jwt = jwt
        self.blend_path = blend_path
        self.target_path = target_path
        self.project_name = project_name

        print('Uploading', project_name)
        print('Spec:')
        print('\t- Number of threads:', number_of_threads)
        print('\t- Chunk size:', chunk_size)
        print('\t- Max retries per chunk:', max_retries_per_chunk)
        sys.stdout.flush()


    def pack(self):
        print('Packing', self.blend_path, 'into', self.target_path)

        try:
            bpath = pathlib.Path(self.blend_path)

            bpath = bpathlib.make_absolute(bpath)
            project_path = bpathlib.make_absolute(bpath).parent

            packer = pack.Packer(bpath, project_path, self.target_path)

            packer.strategise()
            for missing_file in packer.missing_files:
                self.__signal_missing_file(str(missing_file))

            self.__signal_pack_start()
            packer.execute()
            self.__signal_pack_end(True)
        except Exception as error:
            self.__signal_pack_error(str(error))
            self.__signal_pack_end(False)
            sys.exit(1)


    def get_target_size(self) -> int:
        try:
            size = os.path.getsize(self.target_path)
        except Exception as error:
            self.__signal_project_creation_error(error)
            sys.exit(1)
        return size


    def get_nas(self, size: int) -> Tuple[str, str]:
        with Platform(url) as plt:
            try:
                res = plt.get_nas(self.jwt, size, self.project_name, jsonify=True)
                return res['ip'], res['jwt']
            except requests.exceptions.HTTPError as error:
                self.__print(f'Project creation failed : {error.response.status_code} - {error.response.text}')
                self.__signal_project_creation_error(error.response.text)
                sys.exit(1)
            except Exception as error:
                self.__print(f'Project creation failed :', error)
                self.__signal_project_creation_error(error)
                sys.exit(1)


    def start(self, nas_url: str, nas_jwt: str):
        self.__signal_upload_start()

        self.nas_url = nas_url
        self.nas_jwt = nas_jwt

        if not os.path.exists(self.target_path):
            raise Exception(f'{self.target_path} doesn\'t exist')
        elif os.path.isdir(self.target_path):
            for dirname, dirnames, filenames in os.walk(self.target_path):
                for filename in filenames:
                    abspath = os.path.join(dirname, filename)
                    self.jobs.append(UploadJob(abspath, root=self.target_path, chunk_size=self.chunk_size))
        else:
            raise Exception(f'{path} file format not supported')

        self.__print(f'Starting {self.number_of_threads} thread')
        self.pool = multiprocessing.pool.ThreadPool(self.number_of_threads)
        self.pool.map(self.__upload_file, self.jobs)
        self.pool.close()
        self.pool.join()

        self.__print(f'Uploading finished')
        self.__signal_upload_end(not self.stop)


    def __stop(self):
        self.__print('Stopping uploading...')
        self.stop = True


    def __is_already_on_server(self, job: UploadJob) -> bool:
        self.__print(f'Checking if {job.upload_path} is already on server...')
        already_uploaded = False

        headers = {
            'FileName': job.upload_path,
            'Checksum': job.file_checksum,
        }

        with Nas(self.nas_url) as nas:
            try:
                res = nas.check_file(self.nas_jwt, headers)
                already_uploaded = res.status_code == HTTPStatus.OK
            except requests.exceptions.HTTPError as error:
                self.__print(f'Check of {job.upload_path} failed : {error.response.status_code} - {error.response.text}')
            except Exception as error:
                self.__print(f'Check of {job.upload_path} failed :', error)

        return already_uploaded


    def __merge_file(self, job: UploadJob):
        self.__print(f'Merging {job.upload_path}...')

        headers = {
            'FileName': job.upload_path,
            'Checksum': job.file_checksum,
            'TotalChunks': str(job.number_of_chunks),
        }

        with Nas(self.nas_url) as nas:
            try:
                nas.merge_file(self.nas_jwt, headers)
            except requests.exceptions.HTTPError as error:
                self.__print(f'Merge of {job.upload_path} failed : {error.response.status_code} - {error.response.text}')
                self.__signal_upload_error(job, error)
                self.__stop()
            except Exception as error:
                self.__print(f'Merge of {job.upload_path} failed :', error)
                self.__signal_upload_error(job, error)
                self.__stop()


    def __upload_chunk(self, job: UploadJob, data) -> bool:
        self.__print(f'Uploading chunk {job.uploaded_chunks} of {job.upload_path}...')
        success = False

        headers = {
            'FileName': job.upload_path,
            'Checksum': str(zlib.crc32(data)),
            'ChunkNumber': str(job.uploaded_chunks),
        }

        while not success and job.retries <= self.max_retries_per_chunk and not self.stop:
            with Nas(self.nas_url) as nas:
                try:
                    res = nas.upload_chunk(self.nas_jwt, headers, data)
                    success = True
                except requests.exceptions.HTTPError as error:
                    self.__print(f'Chunk {job.uploaded_chunks} of {job.upload_path} uploading failed : {error.response.status_code} - {error.response.text}')
                    job.retries += 1
                    if job.retries > self.max_retries_per_chunk:
                        self.__print(f'Failed to upload {job.upload_path}')
                        self.__signal_upload_error(job, error)
                except Exception as error:
                    self.__print(f'Chunk {job.uploaded_chunks} of {job.upload_path} uploading failed :', error)
                    job.retries += 1
                    if job.retries > self.max_retries_per_chunk:
                        self.__print(f'Failed to upload {job.upload_path}')
                        self.__signal_upload_error(job, error)

        return success


    def __upload_file(self, job: UploadJob):
        if self.stop or self.__is_already_on_server(job):
            self.__print(f'Skipping {job.upload_path}')
            return

        self.__print(f'Uploading {job.upload_path}...')
        self.__signal_upload_progress(job)

        with open(job.path, 'rb') as file:
            while job.uploaded_chunks != job.number_of_chunks and not self.stop:
                job.retries = 0
                data = file.read(self.chunk_size)
                success = self.__upload_chunk(job, data)

                if success:
                    self.__print(f'Successfully uploaded chunk {job.uploaded_chunks} of {job.upload_path}')
                    job.uploaded_chunks += 1
                    self.__signal_upload_progress(job)
                else:
                    self.__stop()
                    break

        if not self.stop:
            self.__merge_file(job)
        self.__print()


    def __signal_pack_start(self):
        self.__print(f'CALLBACK PACK_START {self.__format_blend_path()} {self.__format_target_path()}')


    def __signal_pack_error(self, error):
        self.__print(f'CALLBACK PACK_ERROR {self.__format_blend_path()} {self.__format_target_path()} {str(error)}')


    def __signal_missing_file(self, file):
        self.__print(f'CALLBACK MISSING_FILE {self.__format_blend_path()} {self.__format_target_path()} {file}')


    def __signal_pack_end(self, success: bool):
        self.__print(f'CALLBACK PACK_END {self.__format_blend_path()} {self.__format_target_path()} {str(success)}')


    def __signal_project_creation_error(self, error):
        self.__print(f'CALLBACK PROJECT_CREATION_ERROR {self.project_name.replace(" ", "_")} {str(error)}')


    def __signal_upload_start(self):
        self.__print(f'CALLBACK UPLOAD_START {self.__format_target_path()}')


    def __signal_upload_progress(self, job: UploadJob):
        progress = job.uploaded_chunks / job.number_of_chunks * 100.0
        self.__print(f'CALLBACK UPLOAD_PROGRESS {job.upload_path.replace(" ", "_")} {progress}')


    def __signal_upload_end(self, success: bool):
        self.__print(f'CALLBACK UPLOAD_END {self.__format_target_path()} {str(success)}')


    def __signal_upload_error(self, job: UploadJob, error):
        self.__print(f'CALLBACK UPLOAD_ERROR {job.upload_path.replace(" ", "_")} {str(error)}')


    def __format_target_path(self):
        return self.target_path.replace(" ", "_")


    def __format_blend_path(self):
        return os.path.basename(self.blend_path).replace(" ", "_")


    def __print(self, *msgs):
        print(*msgs)
        sys.stdout.flush()


if __name__ == '__main__':
    failure = True
    try:
        argv = sys.argv[sys.argv.index('--') + 1:]
        if len(argv) != 5:
            print(argv)
            print('Usage: python3 ./uploader.py blend_path target_path project_name url jwt')
            sys.exit(1)
        blend_path, target_path, project_name, url, jwt = argv

        uploader = Uploader(
            blend_path = blend_path,
            target_path = target_path,
            project_name = project_name,
            # Currently, only one thread is supported (for a better UI display and error handling)
            number_of_threads = 1,
            url = url,
            jwt = jwt,
        )

        uploader.pack()

        project_size = uploader.get_target_size()
        nas_url, nas_jwt = uploader.get_nas(project_size)

        uploader.start(nas_url, nas_jwt)

        failure = uploader.stop
    except Exception as error:
        print(f'CALLBACK ERROR {str(error)}')
    finally:
        sys.exit(failure)