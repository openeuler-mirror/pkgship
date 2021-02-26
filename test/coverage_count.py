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
import os
import sys
import unittest

import coverage
from coverage import CoverageException

suite = unittest.TestSuite()
BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(
    os.path.dirname(__file__))), "packageship")
TEST_CASE_PATH = os.path.join(os.path.dirname(BASE_PATH), "test")
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

cov = coverage.coverage(data_suffix='init', include=[BASE_PATH + '/application/*'],
                        omit=["*__init__.py"], data_file='./.coverage')


def specify_case(file_path):
    """
    Test specify test cases
    Args:
        file_path: test cases file path

    Returns: discover result
    """
    discover = unittest.defaultTestLoader.discover(
        file_path, pattern="test*.py", top_level_dir=file_path)
    return discover


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    args = sys.argv
    cov.start()
    test_case_files = [os.path.join(TEST_CASE_PATH, "test_module/test_database/"),
                       os.path.join(TEST_CASE_PATH, "test_module/test_packages/test_database_query/"),
                       os.path.join(TEST_CASE_PATH, "test_module/test_db_priority/"),
                       os.path.join(TEST_CASE_PATH, "test_module/test_packages/test_all_src_package"),
                       os.path.join(TEST_CASE_PATH, "test_module/test_packages/test_all_bin_package"),
                       os.path.join(TEST_CASE_PATH, "test_module/test_basedepend/"),
                       os.path.join(TEST_CASE_PATH, "test_module/test_bedepend/"),
                       ]
    for file in test_case_files:
        runner.run(specify_case(file))
    cov.stop()
    try:
        cov.report(show_missing=True)
        cov.html_report()
    except CoverageException:
        print("No data to report")
