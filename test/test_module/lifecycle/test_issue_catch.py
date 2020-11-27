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
# -*- coding:utf-8 -*-
"""
TestGetIssue

"""
from test.base_code.operate_data_base import OperateTestBase
import unittest
import json

from packageship.application.apps.package.function.constants import ResponseCode


class TestIssueCatch(OperateTestBase):
    """
    Test Get Issue info
    """
    REQUESTS_KWARGS = {
        "url": "/lifeCycle/issuecatch",
        "method": "post",
        "data": "",
        "content_type": "application/json"
    }

    def test_wrong_params(self):
        """
        test issue catch
        """
        error_param = "[]"
        self.REQUESTS_KWARGS["data"] = error_param
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_correct_params(self):
        """
        Correct params
        Returns:

        """
        self.REQUESTS_KWARGS["data"] = json.dumps({
            "hook_name": "issue_hooks",
            "password": "pwd",
            "hook_id": 1,
            "hook_url": "http://gitee.com/liwen/gitos/hooks/1/edit",
            "timestamp": "1576754827988",
            "sign": "rLEHLuZRIQHuTPeXMib9Czoq9dVXO4TsQcmQQHtjXHA=",
            "issue": {
                "html_url": "https://gitee.com/oschina/gitee/issues/IG6E9",
                "id": 295024870,
                "number": "IG8E1",
                "title": "IE fault",
                "body": "js fault",
                "issue_type": "缺陷",
                "state": "open",
                "comments": 0,
                "created_at": "2018-02-07T23:46:46+08:00",
                "updated_at": "2018-02-07T23:46:46+08:00",
                "user": {
                    "id": 1,
                    "login": "robot",
                    "avatar_url": "https://gitee.com/assets/favicon.ico",
                    "html_url": "https://gitee.com/robot",
                    "type": "User",
                    "site_admin": False,
                    "name": "robot",
                    "email": "robot@gitee.com",
                    "username": "robot",
                    "user_name": "robot",
                    "url": "https://gitee.com/robot"
                },
                "labels": [
                    {
                        "id": 827033694,
                        "name": "bug",
                        "color": "d73a4a"
                    }
                ],
                "assignee": {
                    "id": 1,
                    "login": "robot",
                    "avatar_url": "https://gitee.com/assets/favicon.ico",
                    "html_url": "https://gitee.com/robot",
                    "type": "User",
                    "site_admin": False,
                    "name": "robot",
                    "email": "robot@gitee.com",
                    "username": "robot",
                    "user_name": "robot",
                    "url": "https://gitee.com/robot"
                },
                "milestone": {
                    "html_url": "https://gitee.com/oschina/gitee/milestones/1",
                    "id": 3096855,
                    "number": 1,
                    "title": "problem",
                    "description": None,
                    "open_issues": 13,
                    "started_issues": 6,
                    "closed_issues": 31,
                    "approved_issues": 42,
                    "state": "open",
                    "created_at": "2018-02-01T23:46:46+08:00",
                    "updated_at": "2018-02-02T23:46:46+08:00",
                    "due_on": None
                }
            },
            "repository": {
                "id": 120249025,
                "name": "Gitee",
                "path": "Cython",
                "full_name": "China/Gitee",
                "owner": {
                    "id": 1,
                    "login": "robot",
                    "avatar_url": "https://gitee.com/assets/favicon.ico",
                    "html_url": "https://gitee.com/robot",
                    "type": "User",
                    "site_admin": False,
                    "name": "robot",
                    "email": "robot@gitee.com",
                    "username": "robot",
                    "user_name": "robot",
                    "url": "https://gitee.com/robot"
                },
                "private": False,
                "html_url": "https://gitee.com/oschina/gitee",
                "url": "https://gitee.com/oschina/gitee",
                "description": "",
                "fork": False,
                "created_at": "2018-02-05T23:46:46+08:00",
                "updated_at": "2018-02-05T23:46:46+08:00",
                "pushed_at": "2018-02-05T23:46:46+08:00",
                "git_url": "git://gitee.com:oschina/gitee.git",
                "ssh_url": "git@gitee.com:oschina/gitee.git",
                "clone_url": "https://gitee.com/oschina/gitee.git",
                "svn_url": "svn://gitee.com/oschina/gitee",
                "git_http_url": "https://gitee.com/oschina/gitee.git",
                "git_ssh_url": "git@gitee.com:oschina/gitee.git",
                "git_svn_url": "svn://gitee.com/oschina/gitee",
                "homepage": None,
                "stargazers_count": 11,
                "watchers_count": 12,
                "forks_count": 0,
                "language": "ruby",
                "has_issues": True,
                "has_wiki": True,
                "has_pages": False,
                "license": None,
                "open_issues_count": 0,
                "default_branch": "master",
                "namespace": "oschina",
                "name_with_namespace": "China/Gitee",
                "path_with_namespace": "oschina/gitee"
            },
            "sender": {
                "id": 1,
                "login": "robot",
                "avatar_url": "https://gitee.com/assets/favicon.ico",
                "html_url": "https://gitee.com/robot",
                "type": "User",
                "site_admin": False,
                "name": "robot",
                "email": "robot@gitee.com",
                "username": "robot",
                "user_name": "robot",
                "url": "https://gitee.com/robot"
            },
            "enterprise": {
                "name": "oschina",
                "url": "https://gitee.com/oschina"
            }
        })
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(resp_dict, resp_code=ResponseCode.SUCCESS, method=self)


if __name__ == '__main__':
    unittest.main()
