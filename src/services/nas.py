"""This module provides the sdk for Tresorio's Nas."""

# -*- coding: utf-8 -*-
from urllib.parse import urljoin
import logging
import aiohttp


class Nas:
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

    def __init__(self, base_url: str, mocked=False):
        self.url = base_url
        self.mocked = mocked
        self._session = None
        self._logger = logging.getLogger("Nas")
        self._set_logger()

    def _set_logger(self):
        """Configurates the logger for the Nas instance"""
        log_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)-5.5s] %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        self._logger.addHandler(console_handler)

    async def __aenter__(self):
        """Entrypoint of `async with`"""
        return self

    async def __aexit__(self, *args):
        """Callback once out of the `async with` block"""
        if self._session is not None:
            return await self._session.close()

    @staticmethod
    def _nasrequest(func):
        """Wrapper used to skip code duplication over the Nas's methods.

        It will create a new aiohttp client session if there wasn't any before
        (happens when Nas is instanciated outside of an `async with`). It
        also handles the catching of ClientResponseError and the logging of
        this exception.

        Args:
            func: Nas's method to decorate.

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
            if self.mocked is True:
                return await func(*args, **kwargs)
            try:
                if self._session is None:
                    self._session = aiohttp.ClientSession()
                res = await func(self, *args, **kwargs)
                if read is True:
                    return await res.read()
                return res
            except aiohttp.ClientError as err:
                self._logger.error(f'{err}')
                return None
        return wrapper

    @_nasrequest.__func__
    async def download(self, uuid: str, src_filename: str):
        """Downloads a specific file on the Nas.

        Arg:
            uuid: The uuid of the project we want to target.
            src_filename: file to download.

        Example:
            >>> with Nas('http://0.0.0.0:3000') as nas:
            ...     task = await nas.download('55fe2bc6', 'my_file.txt')
            ...     file = asyncio.run(task)
        """
        url = urljoin(self.url, uuid+'/'+src_filename)
        response = await self._session.get(url, raise_for_status=True)
        return response

    @_nasrequest.__func__
    async def download_project(self, uuid: str):
        """Downloads a whole project as a zip

        Arg:
            uuid: The uuid of the project we want to download

        Example:
            >>> with Nas('http://0.0.0.0:3000') as nas:
            ...     task = await nas.list_files('55fe2bc6')
            ...     project = asyncio.run(task)
        """
        url = urljoin(self.url, uuid+"?download=1&format=zip")
        response = await self._session.get(url, raise_for_status=True)
        return response

    @_nasrequest.__func__
    async def list_files(self, uuid: str):
        """Lists the files contained in the Nas specific uuid folder.

        Arg:
            uuid: The uuid of the project we want to list

        Example:
            >>> with Nas('http://0.0.0.0:3000') as nas:
            ...     task = await nas.list_files('55fe2bc6')
            ...     files = asyncio.run(task)
        """
        url = urljoin(self.url, uuid)
        response = await self._session.get(url, raise_for_status=True)
        return response

    @_nasrequest.__func__
    async def upload_content(self, uuid: str, content, filename: str):
        """Uploads any type of content to the Nas targeted by self.url.

        Args:
            uuid: main directory where the content will be stored
            content (str, bytes, fd): content to upload on the Nas
            filename: name of the uploaded file on the Nas

        Example:
            >>> async with Nas('http://0.0.0.0:3000') as nas:
            ...     task = nas.upload_content('55fe2bc6', 'Hello world', 'file.txt')
            ...     asyncio.run(task)
        """
        url = urljoin(self.url, uuid)
        with aiohttp.MultipartWriter('form-data') as mpw:
            header = {
                'Content-Disposition': f'form-data; name="{filename}"; filename="{filename}"'
            }
            mpw.append(content, headers=header)
            response = await self._session.put(url, data=mpw, raise_for_status=True)
            return response

    async def close(self):
        """Closes the aiohttp session. To use if Nas is not instanciated with `async with`."""
        if self._session is not None:
            return await self._session.close()
