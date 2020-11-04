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
 build_depend unittest
"""
from test.base_code.read_data_base import ReadTestBase
import os
import sys


class TestLicence(ReadTestBase):

    def test_licence(self):
        if getattr(sys, 'frozen', False):
            BASE_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))
        else:
            BASE_PATH = os.path.abspath(os.path.dirname(__file__))
            BASE_PATH = BASE_PATH.split("pkgship")[0]
            BASE_PATH = os.path.join(BASE_PATH, 'pkgship')
        self.find_all_py_file([BASE_PATH])


