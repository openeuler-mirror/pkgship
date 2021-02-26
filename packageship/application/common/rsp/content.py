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
    Response content
"""
from .xmlmap import xml


class RspMsg:
    """
        Response content
    """

    def __init__(self, label="success", **kwargs):
        self._label = label
        self.response_body = {
            "message": kwargs.get("message"),
            "resp": None
        }

    def _code(self, label):
        """
            Response Code
        """
        response_body = xml.content(label)
        return response_body

    def _body(self, body, label, zh=False):
        if body:
            if not hasattr(self.response_body, "message") or self.response_body["message"] is None:
                self.response_body["message"] = body["message_zh"] if zh else body["message_en"]
            self.response_body["code"] = body["status_code"]
            if label != "success":
                self.response_body["tip"] = body["tip_zh"] if zh else body["tip_en"]

    def body(self, label, zh=False, **kwargs):
        """
            get the response body
        """
        self.response_body.update(**kwargs)
        self._body(self._code(label), label, zh)
        return self.response_body


rspmsg = RspMsg()
