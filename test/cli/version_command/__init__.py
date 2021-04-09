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
import argparse

from packageship.application.cli.commands.version import VersionCommand
from packageship.application.common.remote import RemoteService
from test.cli import ClientTest


def _init(self):
    """
    Description: Class instance initialization
    """
    super(VersionCommand, self).__init__()

    self.parse = argparse.ArgumentParser()

    self.params = [
        ('-v', 'str', 'Get version information', None, 'store_true'),
        ('-remote', 'str', 'The address of the remote service', False, 'store_true')
    ]

class VersionTest(ClientTest):
    def __init__(self, methodName: str) -> None:
        super(VersionTest, self).__init__(methodName)

    def setUp(self) -> None:
        super(VersionTest, self).setUp()
        self.mock_requests_get(side_effect=self.client.get)
        VersionCommand.__init__ = _init


