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
        Upload a whole folder (in case there are assets for the rendering)
    """

    def __init__(self, base_url: str, mocked=False):
        self.url = base_url
        self.mocked = mocked
        self._session = None
        self._logger = logging.getLogger("Nas")
        self._set_logger()

    def _log_client_co_err(self, exc: aiohttp.ClientConnectionError, prefix: str = ""):
        """Logs the ClientConnectionErrors thanks to the wrapper @nasrequest.

        Args:
            exc: The client connection exception.
            prefix: A string to prepend the logs.
        """
        err = f'{prefix} [{exc.request_info.method}] {exc.args[0]}'
        self._logger.error(err)

    def _set_logger(self):
        """Configurates the logger for the Nas instance"""
        log_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)-5.5s] %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        self._logger.addHandler(console_handler)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
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
            ... def Nas_method(self, uuid):
            ...     pass
        """
        async def wrapper(self, *args, **kwargs):
            if self.mocked is True:
                return await func(*args, **kwargs)
            try:
                if self._session is None:
                    self._session = aiohttp.ClientSession()
                return await func(self, *args, **kwargs)
            except aiohttp.ClientResponseError as exc:
                self._log_client_co_err(
                    exc, prefix=f'{self.__class__.__name__}.{func.__name__}')

        return wrapper

    @_nasrequest.__func__
    async def download(self, uuid: str, src_filename: str):
        url = urljoin(self.url, uuid+'/'+src_filename)
        response = await self._session.get(url, raise_for_status=True)
        return await response.read()

    @_nasrequest.__func__
    async def download_project(self, uuid: str):
        url = urljoin(self.url, uuid+"?download=1&format=zip")
        response = await self._session.get(url, raise_for_status=True)
        return await response.read()

    @_nasrequest.__func__
    async def list_files(self, uuid: str):
        url = urljoin(self.url, uuid)
        response = await self._session.get(url, raise_for_status=True)
        return await response.text()

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
            return await response.text()

    async def close(self):
        """Closes the aiohttp session. To use if Nas is not instanciated with `async with`."""
        if self._session is not None:
            return await self._session.close()
