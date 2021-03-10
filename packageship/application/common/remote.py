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

import requests
from requests.exceptions import RequestException, HTTPError
from retrying import retry


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
        return self._response.content.decode('utf-8') if self._response else None

    def _dispatch(self, method, url, **kwargs):
        """
        Description: Request remote services in different ways

        Args:
            method: request method， GET、 POST 、PUT 、DELETE
            url:Remote request address
            kwargs:parameters associated with the request
        """

        @retry(stop_max_attempt_number=self._retry, stop_max_delay=self._max_delay)
        def http(url):
            response = method(url, **kwargs)
            if response.status_code == requests.codes["too_many_requests"]:
                return response
            elif response.status_code != requests.codes["ok"]:
                _msg = "There is an exception with the remote service [%s]，" \
                       "Please try again later.The HTTP error code is：%s" % (url,
                                                                             str(response.status_code))
                raise HTTPError(_msg)
            else:
                return response

        method = getattr(self, method, None)
        if method is None:
            raise RequestException(
                "Request mode error, temporarily only support POST, GET")
        try:
            self._response = http(url)
        except RequestException as error:
            raise RequestException from error

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
        data = kwargs.get('data') or self._body
        response = requests.post(url=url, data=data, **kwargs)
        return response
