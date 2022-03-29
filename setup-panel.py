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
Package management program installation configuration
file for software packaging
"""
import os

from distutils.sysconfig import get_python_lib
from setuptools import setup, find_packages


PACKAGE_PATH = get_python_lib()
PACKAGESHIP_PATH = os.path.join(PACKAGE_PATH, "packageship_panel")


setup(
    name="packageship-panel",
    version="1.0",
    packages=find_packages(exclude=["test.*", "packageship.*", "packageship", "test"]),
    requires=[
        "packageship(==2.1.0)",
        "aiohttp(==3.8.1)",
        "APScheduler(==3.8.1)",
        "lxml(==4.6.3)",
    ],
    # package_data=["timed_task.yaml", "sig_mentor.yaml"],
    license="The software package builds the data panel",
    long_description=open("README.md", encoding="utf-8").read(),
    author="gongzhengtang",
    data_files=[
        (
            PACKAGESHIP_PATH,
            ["timed_task.yaml", "sig_mentor.yaml"],
        ),
    ],
    zip_safe=False,
)
