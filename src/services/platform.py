import bpy
import json
import asyncio
import logging
from typing import Dict, Any
from typing import Callable, Any
from urllib.parse import urljoin
from bundle_modules import aiohttp
import src.services.async_loop as async_loop
from src.services.loggers import PLATFORM_LOGGER
from src.config.api import API_CONFIG, SSL_CONTEXT


class Platform:

    def __init__(self, mocked=False):
        self.url = API_CONFIG['backend']
        self.mocked = mocked
        self._session = None
        self._logger = PLATFORM_LOGGER

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
            self._logger.debug(f'Entering {func.__name__}')
            if self.mocked is True:
                return await func(*args, **kwargs)
            if self._session is None:
                self._session = aiohttp.ClientSession(conn_timeout=5)
            res = await func(self, *args, **kwargs)
            if jsonify is True:
                return await res.json()
            if read is True:
                return await res.read()
            return res
        return wrapper

    @_platformrequest.__func__
    async def req_connect_to_tresorio(self, credentials: Dict[str, Any]) -> aiohttp.ClientResponse:
        url = urljoin(self.url, API_CONFIG['routes']['signin'])
        return await self._session.post(url, json=credentials, raise_for_status=True, ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_launch_render(self, jwt: str, render_id: str, launch_render: Dict[str, Any]) -> aiohttp.ClientResponse:
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        url = urljoin(
            self.url, API_CONFIG['routes']['launch_render'].format(render_id))
        return await self._session.post(url, json=launch_render, headers=headers, raise_for_status=True, ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_stop_render(self, jwt: str, render_id: str):
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        url = urljoin(
            self.url, API_CONFIG['routes']['stop_render'].format(render_id))
        return await self._session.put(url, headers=headers, raise_for_status=True, ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_delete_render(self, jwt: str, render_id: str):
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        url = urljoin(
            self.url, API_CONFIG['routes']['delete_render'].format(render_id))
        return await self._session.delete(url, headers=headers, raise_for_status=True, ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_get_user_info(self, jwt: str) -> aiohttp.ClientResponse:
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        url = urljoin(self.url, API_CONFIG['routes']['user_info'])
        return await self._session.get(url, raise_for_status=True, headers=headers, ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_get_renderpacks(self, jwt: str) -> aiohttp.ClientResponse:
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        url = urljoin(self.url, API_CONFIG['routes']['renderpacks'])
        return await self._session.get(url, raise_for_status=True, headers=headers, ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_create_render(self, jwt: str, render: Dict[str, Any]):
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        url = urljoin(self.url, API_CONFIG['routes']['create_render'])
        return await self._session.post(url, json=render, raise_for_status=True, headers=headers, ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_list_renderings_details(self, jwt: str):
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        params = {
            'offset': 0,
            'count': 30,
        }
        url = urljoin(
            self.url, API_CONFIG['routes']['list_renderings_details'])
        return await self._session.get(url, params=params, raise_for_status=True, headers=headers, ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_get_rendering_details(self, jwt: str, render_id: str):
        headers = {
            'Authorization': f'JWT {jwt}',
            'Content-Type': 'application/json'
        }
        url = urljoin(
            self.url, API_CONFIG['routes']['rendering_details'].format(render_id))
        return await self._session.get(url, headers=headers, ssl_context=SSL_CONTEXT)

    async def close(self):
        """Closes the aiohttp session."""
        if self._session is not None:
            return await self._session.close()
