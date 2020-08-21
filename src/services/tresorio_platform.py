"""This module provides the sdk for Tresorio's backend"""


from urllib.parse import urljoin
from typing import Dict, Any, Callable, Union

from bundle_modules import aiohttp
from src.services.loggers import PLATFORM_LOGGER
from src.config.api import API_CONFIG, SSL_CONTEXT, MODE

backend_url = API_CONFIG[MODE]['backend']


def set_backend_url(url):
    global backend_url
    backend_url = url


class Platform:
    """Tresorio's asynchronous backend sdk

    Arg:
        mocked (bool): Activates or no the mock. A mock is not interacting
            with the servors, it just mimicks the behavior. Default is False.

    Example:
        >>> async with Platform() as plt:
        ...     credentials = {
        ...         'email': 'tresorio@demo.com',
        ...         'password': 'tresorio'
        ...     }
        ...     res = await plt.req_connect_to_tresorio(credentials)

    """

    def __init__(self,
                 mocked: bool = False):
        self.url = backend_url
        self.mocked = mocked
        self.session = None
        self.logger = PLATFORM_LOGGER

    async def __aenter__(self):
        """Entrypoint of `async with` to init the platform sdk"""
        self.logger.debug('Init of the platform\'s sdk')
        return self

    async def __aexit__(self,
                        *args: Any):
        """Exitpoint of the `async with` block to close the platform sdk"""
        self.logger.debug('Exit of the platform\'s sdk')
        if self.session is not None:
            return await self.session.close()

    @staticmethod
    def _platformrequest(func: Callable[[str, Any], aiohttp.ClientResponse]):
        """Wrapper used to skip code duplication over the Nas's methods.

        It will create a new aiohttp client session if there wasn't any before
        (happens when Nas is instanciated outside of an `async with`). It
        also handles the catching of ClientResponseError and the logging of
        this exception.

        Arg:
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
        async def wrapper(self,
                          *args: Any,
                          read: bool = False,
                          jsonify: bool = False,
                          **kwargs: Any
                          ) -> Union[bytes, Dict[str, Any], aiohttp.ClientResponse]:
            """This wrapper handles common cases of platform requests

            Args:
                read: If `False`, the wrapped function will return the whole
                response. If `True`, will read the response and return bytes
                jsonify (overides `read`): If `False`, will proceed the `read` arg.
                Else, will return the body as a dict.
            """
            self.logger.debug(f'Entering {func.__name__}')
            if self.mocked is True:
                return await func(*args, **kwargs)
            if self.session is None:
                self.session = aiohttp.ClientSession(conn_timeout=5)
            res = await func(self, *args, **kwargs)
            if jsonify is True:
                return await res.json()
            if read is True:
                return await res.read()
            return res
        return wrapper

    @_platformrequest.__func__
    async def req_latest_version(self) -> aiohttp.ClientResponse:
        url = urljoin(self.url, API_CONFIG['routes']['latest_version'])
        return await self.session.get(url,
            raise_for_status=True,
            ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_connect_to_tresorio(self,
                                      credentials: Dict[str, str]
                                      ) -> aiohttp.ClientResponse:
        """Authentificate to Tresorio

        Arg:
            credentials: A dictionnary containing the credentials required
            to connect to Tresorio.

        Example:
            >>> async with Platform() as plt:
            ...     credentials = {
            ...         'email': 'tresorio@demo.com',
            ...         'password': 'tresorio'
            ...     }
            ...     res = await plt.req_connect_to_tresorio(credentials)
        """
        url = urljoin(self.url, API_CONFIG['routes']['signin'])
        return await self.session.post(url,
                                       json=credentials,
                                       raise_for_status=True,
                                       ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_resume_render(self,
                                cookie: str,
                                render_id: str,
                                farm_index: int
                                ) -> aiohttp.ClientResponse:
        url = urljoin(self.url, API_CONFIG['routes']['resume_render'].format(render_id))
        return await self.session.put(url,
                                       json={'farmIndex': farm_index},
                                       headers={'Content-Type': 'application/json'},
                                       cookies={'connect.sid': cookie},
                                       raise_for_status=True,
                                       ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_launch_render(self,
                                cookie: str,
                                launch_render_params: Dict[str, Any]
                                ) -> aiohttp.ClientResponse:
        """Launch a render

        Args:
            cookie: The session cookie given at the connection to
            cookie: The session cookie given at the connection to Tresorio's API.
            render_id: The id of the render to launch.
            launch_render_params: parameters required to launch the rendering

        Example:
            >>> async with Platform() as plt:
            ...     cookie = 'eyJ0eXAiOiJKV1QiLC'
            ...     params = {
            ...         'name': props.rendering_name,
            ...         'engine': props.render_engines_list,
            ...         'outputFormat': props.output_formats_list,
            ...         'timeout': props.timeout,
            ...         'farm': props.render_pack,
            ...         'renderType': render_type,
            ...         'numberOfFarmers': props.nb_farmers,
            ...         'numberOfFrames': number_of_frames,
            ...         'autoTileSize': props.auto_tile_size,
            ...         'currentFrame': 0,
            ...         'startingFrame': 12,
            ...         'endingFrame': 27,
            ...         'projectID': 1,
            ...     }
            ...     res = await plt.req_launch_render(cookie, params)
        """
        url = urljoin(self.url, API_CONFIG['routes']['launch_render'])
        return await self.session.post(url,
                                       json=launch_render_params,
                                       headers={'Content-Type': 'application/json'},
                                       cookies={'connect.sid': cookie},
                                       raise_for_status=True,
                                       ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_stop_render(self,
                              cookie: str,
                              render_id: str
                              ) -> aiohttp.ClientResponse:
        """Stop a render

        Args:
            cookie: The session cookie given at the connection to Tresorio's API.
            render_id: The id of the render to stop.

        Example:
            >>> async with Platform() as plt:
            ...     cookie = 'eyJ0eXAiOiJKV1QiLC'
            ...     render_id = '5c5793e2-055d-11ea-9a9f-362b9e155667'
            ...     res = await plt.req_stop_render(cookie, render_id)
        """
        url = urljoin(self.url,
                      API_CONFIG['routes']['stop_render'].format(render_id))
        return await self.session.put(url,
                                      headers={'Content-Type': 'application/json'},
                                      cookies={'connect.sid': cookie},
                                      raise_for_status=True,
                                      ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_delete_render(self,
                                cookie: str,
                                render_id: str
                                ) -> aiohttp.ClientResponse:
        """Delete a render

        Args:
            cookie: The session cookie given at the connection to Tresorio's API.
            render_id: The id of the render to delete.

        Example:
            >>> async with Platform() as plt:
            ...     cookie = 'eyJ0eXAiOiJKV1QiLC'
            ...     render_id = '5c5793e2-055d-11ea-9a9f-362b9e155667'
            ...     res = await plt.req_delete_render(cookie, render_id)
        """
        url = urljoin(self.url,
                      API_CONFIG['routes']['delete_render'].format(render_id))
        return await self.session.delete(url,
                                         headers={'Content-Type': 'application/json'},
                                         cookies={'connect.sid': cookie},
                                         raise_for_status=True,
                                         ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_get_user_info(self,
                                cookie: str
                                ) -> aiohttp.ClientResponse:
        """Fetch the user information

        Args:
            cookie: The session cookie given at the connection to Tresorio's API.

        Example:
            >>> async with Platform() as plt:
            ...     cookie = 'eyJ0eXAiOiJKV1QiLC'
            ...     res = await plt.req_get_user_info(cookie)
        """
        url = urljoin(self.url, API_CONFIG['routes']['user_info'])
        return await self.session.get(url,
                                      raise_for_status=True,
                                      headers={'Content-Type': 'application/json'},
                                      cookies={'connect.sid': cookie},
                                      ssl_context=SSL_CONTEXT)


    @_platformrequest.__func__
    async def req_create_render(self,
                                cookie: str,
                                renderSize: int,
                                projectName: str
                                ) -> aiohttp.ClientResponse:
        """Create a render

        Args:
            cookie: The session cookie given at the connection to Tresorio's API.

        Example:
            >>> async with Platform() as plt:
            ...     renderSize = 42
            ...     cookie = 'eyJ0eXAiOiJKV1QiLC'
            ...     res = await plt.req_create_render(cookie, renderSize)
        """
        url = urljoin(self.url, API_CONFIG['routes']['create_render'])
        return await self.session.post(url,
                                       json={'size': renderSize, 'name': projectName},
                                       raise_for_status=True,
                                       headers={'Content-Type': 'application/json'},
                                       cookies={'connect.sid': cookie},
                                       ssl_context=SSL_CONTEXT)

    @_platformrequest.__func__
    async def req_list_renderings_details(self,
                                          cookie: str
                                          ) -> aiohttp.ClientResponse:
        """List the renderings of the user

        Args:
            cookie: The session cookie given at the connection to Tresorio's API.

        Example:
            >>> async with Platform() as plt:
            ...     cookie = 'eyJ0eXAiOiJKV1QiLC'
            ...     res = await plt.req_list_renderings_details(cookie)
        """
        params = {
            'offset': 0,
            'count': 100,
        }
        url = urljoin(
            self.url, API_CONFIG['routes']['list_renderings_details'])
        return await self.session.get(url,
                                      params=params,
                                      raise_for_status=True,
                                      headers={'Content-Type': 'application/json'},
                                      cookies={'connect.sid': cookie},
                                      ssl_context=SSL_CONTEXT)


    @_platformrequest.__func__
    async def req_get_farms(self,
        cookie: str,
        params: Dict[str, Any]
    ) -> aiohttp.ClientResponse:
        url = urljoin(self.url,
            API_CONFIG['routes']['farms'])
        return await self.session.get(url,
                                      headers={'Content-Type': 'application/json'},
                                      cookies={'connect.sid': cookie},
                                      json=params,
                                      ssl_context=SSL_CONTEXT)


    @_platformrequest.__func__
    async def req_get_rendering_details(self,
                                        cookie: str,
                                        render_id: str
                                        ) -> aiohttp.ClientResponse:
        """Fetch the details of a specific rendering

        Args:
            cookie: The session cookie given at the connection to Tresorio's API.
            render_id: The unique id of the render to fetch

        Example:
            >>> async with Platform() as plt:
            ...     cookie = 'eyJ0eXAiOiJKV1QiLC'
            ...     render_id = '23kze239'
            ...     res = await plt.req_get_rendering_details(cookie, render_id)
        """
        url = urljoin(self.url,
                      API_CONFIG['routes']['rendering_details'].format(render_id))
        return await self.session.get(url,
                                      headers={'Content-Type': 'application/json'},
                                      cookies={'connect.sid': cookie},
                                      ssl_context=SSL_CONTEXT)

    async def close(self):
        """Closes the aiohttp session."""
        if self.session is not None:
            return await self.session.close()
