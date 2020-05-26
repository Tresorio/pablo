"""This module provides the sdks for Tresorio's Nas."""

from io import TextIOWrapper
from urllib.parse import urljoin
from typing import Callable, Any, Union
import shutil
import requests

from bundle_modules import aiohttp, certifi
from src.config.api import SSL_CONTEXT
from src.services.loggers import NAS_LOGGER


class AsyncNas:
    """Tresorio's Nas asynchronous sdk

    Args:
        base_url (str): The url of the Nas with which to interact.
        mocked (bool): Activates or no the mock. A mock is not interacting
            with the servors, it just mimicks the behavior. Default is False.

    Examples:
        This example shows the way to setup a Nas instance that will
        interact with the Nas API:

        >>> nas = Nas('http://0.0.0.0:3000')

        This one shows the way to mock the behavior of the Nas Api:

        >>> nas = Nas(mocked=True)

        The __aenter__ and __aexit__ allow the use of async with:

        >>> async with Nas('http://0.0.0.0:3000') as nas:
        ...     nas.download('uuid', 'file.txt')

    TODO's:
        - Upload a whole folder (in case there are assets for the rendering / simulation)
        - Write the mocked part of the @_nasrequests methods
    """

    def __init__(self,
                 base_url: str = '',
                 mocked: bool = False):
        self.url = base_url
        self.mocked = mocked
        self.session = None
        self.logger = NAS_LOGGER

    async def __aenter__(self):
        """Entrypoint of `async with` to init the nas sdk"""
        self.logger.debug('Init of the nas\'s sdk')
        return self

    async def __aexit__(self,
                        *args: Any):
        """Exitpoint of the `async with` block to close the nas sdk"""
        self.logger.debug('Exit of the nas\'s sdk')
        if self.session is not None:
            return await self.session.close()

    @staticmethod
    def _nasrequest(func: Callable[[Any], aiohttp.ClientResponse]):
        """Wrapper used to skip code duplication over the Nas's methods

        It will create a new aiohttp client session if there wasn't any before
        (happens when Nas is instanciated outside of an `async with`).

        Arg:
            func: Nas's method to decorate.args

        Return:
            The newly decorated function.

        Example:
            As _nasrequest is a @staticmethod, we need to access its function
            with __func__.

            >>> @_nasrequest.__func__
            ... async def Nas_method(self, uuid):
            ...     pass
        """
        async def _wrapper(self,
                           *args: Any,
                           read: bool = False,
                           **kwargs: Any
                           ) -> Union[aiohttp.ClientResponse, bytes]:
            """This wrapper handles common cases of nas requests

            Args:
                read: If `False`, the wrapped function will return the whole
                    response. If `True`, will read the response and return bytes
            """
            self.logger.debug(f'[ASYNC] Entering {func.__name__}')
            if self.mocked is True:
                return await func(*args, **kwargs)
            if self.session is None:
                self.session = aiohttp.ClientSession(conn_timeout=15)
            res = await func(self, *args, **kwargs)
            if read is True:
                return await res.read()
            return res
        return _wrapper

    @_nasrequest.__func__
    async def download(self,
                       jwt: str,
                       folder: str = '',
                       ) -> aiohttp.ClientResponse:
        """Download a whole project as a zip

        Arg:
            jwt: The JWT generated for the project we want to download

        Example:
            >>> async with Nas('http://0.0.0.0:3000') as nas:
            ...     task = await nas.list_files('55fe2bc6')
            ...     project = asyncio.run(task)
        """
        headers = {
            'Authorization': f'JWT {jwt}'
        }
        url = urljoin(self.url, f'/project/{folder}?download=1&format=zip')
        return await self.session.get(url,
                                      headers=headers,
                                      raise_for_status=True,
                                      ssl_context=SSL_CONTEXT)

    @_nasrequest.__func__
    async def list_files(self,
                         jwt: str
                         ) -> aiohttp.ClientResponse:
        """List the files contained in the Nas specific uuid folder

        Arg:
            jwt: The JWT containing the uuid of the project we want to list

        Example:
            >>> async with Nas('http://0.0.0.0:3000') as nas:
            ...     task = await nas.list_files('55fe2bc6')
            ...     files = asyncio.run(task)
        """
        headers = {
            'Authorization': f'JWT {jwt}'
        }
        url = urljoin(self.url, 'project')
        return await self.session.get(url,
                                      headers=headers,
                                      raise_for_status=True,
                                      ssl_context=SSL_CONTEXT)

    @_nasrequest.__func__
    async def upload_content(self,
                             jwt: str,
                             filename: str,
                             content: Union[str, bytes, TextIOWrapper]
                             ) -> aiohttp.ClientResponse:
        """Upload any type of content to the Nas targeted by self.url

        Args:
            uuid: The id of the project on which the content will be uploaded
            jwt: JWT containing the authorizations to upload the content
            content (str, bytes, fd): content to upload on the Nas
            filename: name of the uploaded file on the Nas

        Example:
            >>> async with Nas('http://0.0.0.0:3000') as nas:
            ...     task = nas.upload_content('55fe2bc6', 'file.txt', 'Hello world')
            ...     asyncio.run(task)
        """
        headers = {
            'Authorization': f'JWT {jwt}'
        }
        url = urljoin(self.url, '/project')
        with aiohttp.MultipartWriter('form-data') as mpw:
            header = {
                'Content-Disposition': f'form-data; name="{filename}"; filename="{filename}"'
            }
            mpw.append(content, headers=header)
            return await self.session.put(url,
                                          headers=headers,
                                          data=mpw,
                                          raise_for_status=True,
                                          ssl_context=SSL_CONTEXT)

    async def close(self):
        """Close the aiohttp session. To use if Nas is not instanciated with `async with`."""
        if self.session is not None:
            return await self.session.close()


class SyncNas:
    """Tresorio's Nas synchronous sdk.

    Args:
        base_url (str): The url of the Nas with which to interact.
        mocked (bool): Activates or no the mock. A mock is not interacting
            with the servors, it just mimicks the behavior. Default is False.

    Examples:
        This example shows the way to setup a Nas instance that will
        interact with the Nas API:

        >>> nas = Nas('http://0.0.0.0:3000')

        This one shows the way to mock the behavior of the Nas Api:

        >>> nas = Nas(mocked=True)

        The __enter__ and __exit__ allow the use of with:

        >>> with Nas('http://0.0.0.0:3000') as nas:
        ...     nas.download('uuid', 'file.txt')

    """

    def __init__(self,
                 base_url: str = '',
                 mocked: bool = False):
        self.url = base_url
        self.mocked = mocked
        self.session = None
        self.logger = NAS_LOGGER

    def __enter__(self):
        """Entrypoint of `with`"""
        return self

    def __exit__(self,
                 *args: Any):
        """Callback once out of the `with` block"""
        if self.session is not None:
            self.session.close()

    @staticmethod
    def _nasrequest(func: Callable[[Any], requests.Response]):
        """Wrapper used to skip code duplication over the Nas's methods.

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
        """

        def wrapper(self,
                    *args: Any,
                    read: bool = False,
                    **kwargs: Any
                    ) -> Union[requests.Response, bytes, None]:
            """This wrapper handles common cases of nas requests

            Arg:
                read: If `False`, the wrapped function will return the whole
                    response. If `True`, will read the response and return bytes
            """
            self.logger.debug(f'[SYNC] Entering {func.__name__}')
            if self.mocked is True:
                return func(*args, **kwargs)
            if self.session is None:
                self.session = requests.sessions.Session()
            res = func(self, *args, **kwargs)
            res.raise_for_status()
            if read is True:
                return res.content
            return res
        return wrapper

    @_nasrequest.__func__
    def download(self,
                 jwt: str,
                 folder: str = '',
                 ) -> Union[requests.Response, None]:
        """Download a whole project as a zip

        Arg:
            jwt: jwt: The JWT generated for the project we want to download

        Example:
            >>> with Nas('http://0.0.0.0:3000') as nas:
            ...     res = nas.list_files('55fe2bc6', read=True)
        """
        headers = {
            'Authorization': f'JWT {jwt}'
        }
        url = urljoin(self.url, f'/project/{folder}?download=1&format=zip')
        return self.session.get(url,
                                headers=headers,
                                verify=True,
                                stream=True)

    @_nasrequest.__func__
    def list_files(self,
                   jwt: str
                   ) -> requests.Response:
        """List the files contained in the Nas specific uuid folder.

        Arg:
            jwt: The JWT containing the uuid of the project we want to list

        Example:
            >>> with Nas('http://0.0.0.0:3000') as nas:
            ...     res = nas.list_files('55fe2bc6', read=True)
        """
        headers = {
            'Authorization': f'JWT {jwt}'
        }
        url = urljoin(self.url, 'project/')
        return self.session.get(url,
                                headers=headers,
                                verify=True)

    @_nasrequest.__func__
    def upload_chunk(self,
                    jwt: str,
                    headers: str,
                    data,
                    ) -> requests.Response:
        headers['Authorization'] = f'JWT {jwt}'
        url = urljoin(self.url, '/chunk')
        return self.session.post(url,
                                headers=headers,
                                data=data,
                                verify=True)

    @_nasrequest.__func__
    def check_file(self,
                    jwt: str,
                    headers: str,
                    ) -> requests.Response:
        headers['Authorization'] = f'JWT {jwt}'
        url = urljoin(self.url, '/chunk')
        return self.session.get(url,
                                headers=headers,
                                verify=True)


    @_nasrequest.__func__
    def merge_file(self,
                    jwt: str,
                    headers: str,
                    ) -> requests.Response:
        headers['Authorization'] = f'JWT {jwt}'
        url = urljoin(self.url, '/chunkend')
        return self.session.get(url,
                                headers=headers,
                                verify=True)


    @_nasrequest.__func__
    def upload_content(self,
                       jwt: str,
                       filename: str,
                       content: TextIOWrapper
                       ) -> requests.Response:
        """Upload any type of content to the Nas targeted by self.url.

        Args:
            uuid: The id of the project on which we will upload the content
            jwt: JWT containing the authorizations to upload the content
            content: file descriptor of the file to upload on the Nas
            filename: name of the uploaded file on the Nas

        Example:
            >>> with Nas('http://0.0.0.0:3000') as nas:
            ...     res = nas.upload_content('55fe2bc6', 'Hello world', 'file.txt')
        """
        headers = {
            'Authorization': f'JWT {jwt}'
        }
        url = urljoin(self.url, '/project')
        data = {filename: content}
        return self.session.put(url,
                                headers=headers,
                                data=data,
                                stream=True,
                                verify=True)

    def close(self):
        """Close the aiohttp session. To use if Nas is not instanciated with `with`."""
        if self.session is not None:
            self.session.close()
