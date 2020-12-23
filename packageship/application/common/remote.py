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
"""
    common remote service class
"""

class RemoteService:
    """
        common remote service class
    """
    @property
    def status_code(self):
        """
            get the status code
        """
        pass

    @property
    def content(self):
        """
            undecoded original content
        """
        pass

    @property
    def text(self):
        """
            response content after decode
        """
        pass

    @property
    def response_headers(self):
        """
         get response heaader
        """
        pass

    @classmethod
    def dispatch(cls, method, url, **kwargs):
        """
            diff request methods are executed by mapping
            :param method: request method， GET、 POST 、PUT 、DELETE
            :param url: remote download url
            :param kwargs: related param for remoting requests
            :param kwargs.request_body: request body content
        """
        pass

    def request(self, url, method, request_body=None, retry=3, **kwargs):
        """
            request remote service
        :param url: remote url
        :param method: request method
        :param request_body:reuqest content
        :param retry:default times for failed retrying
        :param kwargs: related param for request
        """
        pass

    def get(self, url, **kwargs):
        """
        http get request
        """
        pass

    def post(self, url, **kwargs):
        """
        http post request
        """
        pass
