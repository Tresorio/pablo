"""This module provides the sdk for Tresorio's Nas."""

import requests
from bundle_modules import aiohttp
from urllib.parse import urljoin
from typing import Callable, Any
from src.services.loggers import NAS_LOGGER


class AsyncNas:
    """Nas's asynchronous sdk.

    Args:
        base_url (str): The url of the Nas with which to interact.
        mocked (bool): Activates or no the mock. A mock is not interacting
            with the servors, it just mimicks its behavior. Default is False.

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
        - Upload a whole folder (in case there are assets for the rendering)
        - Write the mocked part of the @_nasrequests methods
        - Stream upload ?
    """

    def __init__(self, base_url: str, mocked: bool = False):
        self.url = base_url
        self.mocked = mocked
        self._session = None
        self._logger = NAS_LOGGER

    async def __aenter__(self):
        """Entrypoint of `async with`"""
        return self

    async def __aexit__(self, *args):
        """Callback once out of the `async with` block"""
        if self._session is not None:
            return await self._session.close()

    @staticmethod
    def _nasrequest(func: Callable[[str, Any], aiohttp.ClientResponse]):
        """Wrapper used to skip code duplication over the Nas's methods.

        It will create a new aiohttp client session if there wasn't any before
        (happens when Nas is instanciated outside of an `async with`).

        Args:
            func: Nas's method to decorate.args

        Returns:
            The newly decorated function.

        Example:
            As _nasrequest is a @staticmethod, we need to access its function
            with __func__.

            >>> @_nasrequest.__func__
            ... async def Nas_method(self, uuid):
            ...     pass
        """
        async def wrapper(self, *args, read: bool = False, **kwargs):
            """This wrapper handles common cases of nas requests

            Args:
                read: If `False`, the wrapped function will return the whole
                    response. If `True`, will read the response and return bytes
            """
            self._logger.debug(f'[ASYNC] Entering {func.__name__}')
            if self.mocked is True:
                return await func(*args, **kwargs)
            if self._session is None:
                self._session = aiohttp.ClientSession(conn_timeout=5)
            res = await func(self, *args, **kwargs)
            if read is True:
                return await res.read()
            return res
        return wrapper

    @_nasrequest.__func__
    async def download(self, uuid: str, src_filename: str) -> aiohttp.ClientResponse:
        """Downloads a specific file on the Nas.

        Arg:
            uuid: The uuid of the project we want to target.
            src_filename: file to download.

        Example:
            >>> async with Nas('http://0.0.0.0:3000') as nas:
            ...     task = await nas.download('55fe2bc6', 'my_file.txt')
            ...     file = asyncio.run(task)
        """
        url = urljoin(self.url, uuid+'/'+src_filename)
        return await self._session.get(url, raise_for_status=True)

    @_nasrequest.__func__
    async def download_project(self, uuid: str) -> aiohttp.ClientResponse:
        """Downloads a whole project as a zip

        Arg:
            uuid: The uuid of the project we want to download

        Example:
            >>> async with Nas('http://0.0.0.0:3000') as nas:
            ...     task = await nas.list_files('55fe2bc6')
            ...     project = asyncio.run(task)
        """
        url = urljoin(self.url, uuid+"?download=1&format=zip")
        return await self._session.get(url, raise_for_status=True)

    @_nasrequest.__func__
    async def list_files(self, uuid: str) -> aiohttp.ClientResponse:
        """Lists the files contained in the Nas specific uuid folder.

        Arg:
            uuid: The uuid of the project we want to list

        Example:
            >>> async with Nas('http://0.0.0.0:3000') as nas:
            ...     task = await nas.list_files('55fe2bc6')
            ...     files = asyncio.run(task)
        """
        url = urljoin(self.url, uuid)
        return await self._session.get(url, raise_for_status=True)

    @_nasrequest.__func__
    async def upload_content(self, uuid: str, content, filename: str, jwt: str) -> aiohttp.ClientResponse:
        """Uploads any type of content to the Nas targeted by self.url.

        Args:
            uuid: main directory where the content will be stored
            content (str, bytes, fd): content to upload on the Nas
            filename: name of the uploaded file on the Nas
            jwt: write authorization token on Nas

        Example:
            >>> async with Nas('http://0.0.0.0:3000') as nas:
            ...     task = nas.upload_content('55fe2bc6', 'Hello world', 'file.txt')
            ...     asyncio.run(task)
        """
        url = urljoin(self.url, uuid)
        with aiohttp.MultipartWriter('form-data') as mpw:
            header = {
                'Authorization': f'JWT {jwt}',
                'Content-Disposition': f'form-data; name="{filename}"; filename="{filename}"'
            }
            mpw.append(content, headers=header)
            return await self._session.put(url, data=mpw, raise_for_status=True)

    async def close(self):
        """Closes the aiohttp session. To use if Nas is not instanciated with `async with`."""
        if self._session is not None:
            return await self._session.close()


class SyncNas:
    """Nas's synchronous sdk.

    Args:
        base_url (str): The url of the Nas with which to interact.
        mocked (bool): Activates or no the mock. A mock is not interacting
            with the servors, it just mimicks its behavior. Default is False.

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

    def __init__(self, base_url: str, mocked: bool = False):
        self.url = base_url
        self.mocked = mocked
        self._session = None
        self._logger = NAS_LOGGER

    def __enter__(self):
        """Entrypoint of `with`"""
        return self

    def __exit__(self, *args):
        """Callback once out of the `with` block"""
        if self._session is not None:
            return self._session.close()

    @staticmethod
    def _nasrequest(func: Callable[[str, Any], requests.Response]):
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

        def wrapper(self, *args, read: bool = False, **kwargs):
            """This wrapper handles common cases of nas requests

            Args:
                read: If `False`, the wrapped function will return the whole
                    response. If `True`, will read the response and return bytes
            """
            self._logger.debug(f'[SYNC] Entering {func.__name__}')
            if self.mocked is True:
                return func(*args, **kwargs)
            if self._session is None:
                self._session = requests.sessions.Session()
            res = func(self, *args, **kwargs)
            res.raise_for_status()
            if read is True:
                return res.content
            return res
        return wrapper

    @_nasrequest.__func__
    def download(self, uuid: str, src_filename: str) -> requests.Response:
        """Downloads a specific file on the Nas.

        Arg:
            uuid: The uuid of the project we want to target.
            src_filename: file to download.

        Example:
            >>> with Nas('http://0.0.0.0:3000') as nas:
            ...     res = nas.download('55fe2bc6', 'my_file.txt', read=True)
        """
        url = urljoin(self.url, uuid+'/'+src_filename)
        return self._session.get(url)

    @_nasrequest.__func__
    def download_project(self, uuid: str) -> requests.Response:
        """Downloads a whole project as a zip

        Arg:
            uuid: The uuid of the project we want to download

        Example:
            >>> with Nas('http://0.0.0.0:3000') as nas:
            ...     res = nas.list_files('55fe2bc6', read=True)
        """
        url = urljoin(self.url, uuid+"?download=1&format=zip")
        return self._session.get(url)

    @_nasrequest.__func__
    def list_files(self, uuid: str) -> requests.Response:
        """Lists the files contained in the Nas specific uuid folder.

        Arg:
            uuid: The uuid of the project we want to list

        Example:
            >>> with Nas('http://0.0.0.0:3000') as nas:
            ...     res = nas.list_files('55fe2bc6', read=True)
        """
        url = urljoin(self.url, uuid)
        return self._session.get(url)

    @_nasrequest.__func__
    def upload_content(self, uuid: str, fd, filename: str, jwt: str) -> requests.Response:
        """Uploads any type of content to the Nas targeted by self.url.

        Args:
            uuid: main directory where the content will be stored
            fd: file descriptor of the file to upload on the Nas
            filename: name of the uploaded file on the Nas
            jwt: write authorization token on Nas

        Example:
            >>> with Nas('http://0.0.0.0:3000') as nas:
            ...     res = nas.upload_content('55fe2bc6', 'Hello world', 'file.txt')
        """
        url = urljoin(self.url, uuid)
        content = {filename: fd}
        return self._session.put(url, files=content)

    def close(self):
        """Closes the aiohttp session. To use if Nas is not instanciated with `with`."""
        if self._session is not None:
            return self._session.close()
