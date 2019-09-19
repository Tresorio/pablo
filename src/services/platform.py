import bpy
import json
import asyncio
import logging
import aiohttp
from typing import Callable, Any
from urllib.parse import urljoin
from src.config.api import API_CONFIG
import src.services.async_loop as async_loop

logging.basicConfig(level=logging.FATAL)

class Platform:

    def __init__(self, mocked=False):
        self.url = API_CONFIG['backend']
        self.mocked = mocked
        self._session = None
        self._logger = logging.getLogger("Platform")
        self._set_logger()

    def _set_logger(self):
        """Configurates the logger for the Platform instance"""
        log_formatter = logging.Formatter(
            "[PLATFORM][%(asctime)s] [%(levelname)-5.5s] %(message)s")
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
    def _platformrequest(func: Callable[[str, Any], aiohttp.ClientResponse]):
        """Wrapper used to skip code duplication over the Nas's methods.

        It will create a new aiohttp client session if there wasn't any before
        (happens when Nas is instanciated outside of an `async with`). It
        also handles the catching of ClientResponseError and the logging of
        this exception.

        Args:
            func: Platform's method to decorate.

        Returns:
            The newly decorated function.

        Example:
            As _platformrequest is a @staticmethod, we need to access its function
            with __func__.

            >>> @_platformrequest.__func__
            ... async def platform_method(self, *arg):
            ...     pass
        """
        async def wrapper(self, *args, read: bool = False, jsonify: bool = False, **kwargs):
            """This wrapper handles common cases of platform requests

            Args:
                read: If `False`, the wrapped function will return the whole
                    response. If `True`, will read the response and return bytes
                jsonify (overides `read`): If `False`, will proceed the `read` arg.
                    Else, will return the body as a dict.
            """
            if self.mocked is True:
                return await func(*args, **kwargs)
            try:
                if self._session is None:
                    self._session = aiohttp.ClientSession()
                res = await func(self, *args, **kwargs)
                if jsonify is True:
                    return await res.json()
                if read is True:
                    return await res.read()
                return res
            except aiohttp.ClientError as err:
                self._logger.error(f'{err}')
                return None
        return wrapper

    @_platformrequest.__func__
    async def req_connect_to_tresorio(self, credentials: dict) -> aiohttp.ClientResponse:
        url = urljoin(self.url, API_CONFIG['routes']['signin'])
        return await self._session.post(url, data=credentials, raise_for_status=True)

    @_platformrequest.__func__
    async def req_create_render(self, jwt: str, render_desc: dict) -> aiohttp.ClientResponse:
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        url = urljoin(self.url, API_CONFIG['routes']['create_render'])
        print(render_desc)
        return await self._session.post(url, data=render_desc, headers=headers, raise_for_status=True)

    @_platformrequest.__func__
    async def req_get_user_info(self, jwt: str) -> aiohttp.ClientResponse:
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        url = urljoin(self.url, API_CONFIG['routes']['user_info'])
        return await self._session.get(url, raise_for_status=True, headers=headers)

    @_platformrequest.__func__
    async def req_get_renderpacks(self, jwt: str) -> aiohttp.ClientResponse:
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        url = urljoin(self.url, API_CONFIG['routes']['renderpacks'])
        return await self._session.get(url, raise_for_status=True, headers=headers)

    async def close(self):
        """Closes the aiohttp session."""
        if self._session is not None:
            return await self._session.close()
