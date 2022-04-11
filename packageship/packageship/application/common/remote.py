#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import json
import functools
import asyncio
import requests
from requests.exceptions import RequestException
from retrying import retry
import aiohttp
from packageship.application.common.constant import CALL_MAX_DELAY, MAX_RETRY, MAX_DELAY


def async_retry(stop_max_attempt_number=MAX_RETRY):
    """
    Asynchronous retry decorator
    :param stop_max_attempt_number: Maximum number of retries. Default is three
    """

    def wrap(func):
        @functools.wraps(func)
        async def wrap_func(*args, **kwargs):
            number = stop_max_attempt_number
            while True:
                error = None
                try:
                    return await func(*args, **kwargs)
                except (
                    aiohttp.ClientError,
                    asyncio.exceptions.TimeoutError,
                ) as _error:
                    number = number - 1
                    error = _error
                finally:
                    if error and number <= 0:
                        raise error

        return wrap_func

    return wrap


class RemoteService:
    """
    HTTP request service

    Attributes:
        _max_delay:Maximum interval time
        _retry:Retry count
        _body:Request body
        _response:Response info
        _request_error: request error
    """

    def __init__(self, max_delay=1000):
        self._retry = 3
        if not isinstance(max_delay, int):
            max_delay = 1000
        self._max_delay = max_delay
        self._body = None
        self._response = None
        self._request_error = None

    @property
    def status_code(self):
        """
        Description: status code of the response
        """
        if self._response is None:
            return requests.codes["internal_server_error"]
        return self._response.status_code

    @property
    def content(self):
        """
        Description: original content of the response
        """
        return self._response.content if self._response else None

    @property
    def text(self):
        """
        Description: content of the decoded response
        """
        return self._response.content.decode("utf-8") if self._response else None

    def _dispatch(self, method, url, **kwargs):
        """
        Description: Request remote services in different ways

        Args:
            method: request method, GET、 POST 、PUT 、DELETE
            url:Remote request address
            kwargs:parameters associated with the request
        """

        @retry(stop_max_attempt_number=self._retry, stop_max_delay=self._max_delay)
        def http(url):
            response = method(url, **kwargs)

            if response.status_code not in [
                requests.codes["ok"],
                requests.codes["too_many_requests"],
            ]:
                _msg = (
                    "There is an exception with the remote service [%s]，"
                    "Please try again later.The HTTP error code is：%s"
                    % (url, str(response.status_code))
                )
                raise requests.exceptions.HTTPError(_msg)
            return response

        method = getattr(self, method, None)
        if method is None:
            raise RequestException(
                "Request mode error, temporarily only support POST, GET"
            )
        self._response = http(url)

    def request(self, url, method, body=None, max_retry=3, **kwargs):
        """
        Description: Request a remote http service

        Args:
            url: http service address
            method: mode of request ,only GET、 POST、 DELETE、 PUT is supported
            body: Request body content
            max_retry: The number of times the request failed to retry
            kwargs: Request the relevant parameters
        """
        if not isinstance(max_retry, int):
            max_retry = 3
        self._retry = max_retry
        self._body = body
        try:
            self._dispatch(method=method, url=url, **kwargs)
        except RequestException as error:
            self._request_error = str(error)

    def get(self, url, **kwargs):
        """
        Description: HTTP get request method

        Args:
            kwargs: requests parameters
            url: requested remote address
        """
        response = requests.get(url=url, **kwargs)
        return response

    def post(self, url, **kwargs):
        """
        Description: HTTP post request method

        Args:
            kwargs: requests parameters
            url: requested remote address
        """
        data = kwargs.get("data") or self._body
        response = requests.post(url=url, data=data, **kwargs)
        return response


class Response:
    """http response"""

    def __init__(
        self, error=None, response: aiohttp.ClientResponse = None, text=None
    ) -> None:
        self.error = error
        self.response = response
        self.text = text

    @property
    def success(self):
        """Request the results"""
        return self.response and (
            self.response.status == 200 or self.response.status == 201
        )

    @property
    def status_code(self):
        """response status code"""
        return self.response.status if self.response and self.response.status else 400

    @property
    def json(self):
        """response json"""
        if not all([self.response, self.text]):
            return None
        try:
            return json.loads(self.text)
        except json.JSONDecodeError:
            return None

    @property
    def headers(self):
        """response header"""
        return dict() if not self.response else self.response.headers


class AsyncRequest:
    """
    async http request
    """

    session = None

    def __init__(self, max_attempt_number=MAX_RETRY, stop_max_delay=MAX_DELAY) -> None:
        if self.session is None:
            self.session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
            )
        self._max_attempt_number = max_attempt_number
        self._stop_max_delay = stop_max_delay
        self._response = Response()
        self._agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/97.0.4692.99 Safari/537.36"
        )

    @staticmethod
    def __init_params(**kwargs):
        default_attribute = dict(max_attempt_number=MAX_RETRY, stop_max_delay=MAX_DELAY)
        return {
            attribute: kwargs.get(attribute, val)
            for attribute, val in default_attribute.items()
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.session.close()

    @property
    def headers(self):
        """request header"""
        headers = {"User-Agent": self._agent}
        return headers

    def _set_headers(self, request_header):
        if "headers" not in request_header:
            request_header["headers"] = self.headers
        request_header["headers"].setdefault("User-Agent", self._agent)
        request_header["headers"].setdefault("Content-Type", "application/json")

    async def _get(self, url, params=None, **kwargs):
        self._set_headers(request_header=kwargs)

        @async_retry(stop_max_attempt_number=self._max_attempt_number)
        async def _http_request():
            return await self.session.get(
                url, params=params, timeout=CALL_MAX_DELAY, **kwargs
            )

        await self._request(_http_request)

    @classmethod
    async def get(cls, url, **kwargs) -> "Response":
        """request get
        :param url: request url
        """
        async with cls(**cls.__init_params(**kwargs)) as self:
            await getattr(self, "_get")(url, **kwargs)
            return getattr(self, "_response")

    async def _request(self, http_request):
        try:
            self._response.response = await http_request()
            self._response.text = await self._response.response.text()
        except (
            aiohttp.ClientError,
            asyncio.exceptions.TimeoutError,
        ) as error:
            self._response.error = error

    async def _post(self, url, data=None, **kwargs):
        self._set_headers(request_header=kwargs)

        @async_retry(stop_max_attempt_number=self._max_attempt_number)
        async def _http_request():
            return await self.session.post(
                url, data=data, timeout=CALL_MAX_DELAY, **kwargs
            )

        await self._request(_http_request)

    @classmethod
    async def post(cls, url, data=None, **kwargs) -> "Response":
        """request post
        :param url: request url
        :param data: request body
        """
        async with cls(**cls.__init_params(**kwargs)) as self:
            await getattr(self, "_post")(url, data, **kwargs)
            return getattr(self, "_response")


__all__ = ("RemoteService", "AsyncRequest")
