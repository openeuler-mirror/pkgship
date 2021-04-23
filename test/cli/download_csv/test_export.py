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
Test export
"""
import os

import unittest

from packageship.application.common.export import CompressIo


class TestExport(unittest.TestCase):
    export_test_folder = os.path.join(os.path.dirname(
        __file__), "csv_data", "export_test_folder")

    def tearDown(self) -> None:
        """
        creat folder
        """
        os.makedirs(self.export_test_folder, exist_ok=True)
        csv_file = os.path.join(self.export_test_folder, "test.csv")
        with open(csv_file, "w", encoding="utf-8") as csv_file:
            csv_file.write("CUnit")

    def test_export(self):
        """
        test_export
        """
        compress = CompressIo()
        compress_bytes = compress.send_memory_file(self.export_test_folder)
        self.assertIsNotNone(compress_bytes)
