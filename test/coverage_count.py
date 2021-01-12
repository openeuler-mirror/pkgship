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
Statistical coverage
"""

import unittest
import os
import coverage
from coverage import CoverageException


base_path = os.path.join(os.path.dirname(os.path.abspath(
    os.path.dirname(__file__))), "packageship")

suite = unittest.TestSuite()

cov = coverage.coverage(
    data_suffix='init',
    include=[
        base_path + '/*'],
    omit=["*__init__.py"],
    data_file='./.coverage')


def all_case():
    """
    Args:

    Returns:
        All test cases
    """
    discover = unittest.defaultTestLoader.discover(
        ".", pattern="test*.py", top_level_dir=None)
    return discover


if __name__ == "__main__":

    runner = unittest.TextTestRunner()
    cov.start()
    runner.run(all_case())
    cov.stop()
    try:
        cov.report(show_missing=True)
        cov.html_report()
    except CoverageException:
        print("No data to report")
