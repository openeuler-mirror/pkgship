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

setup(
    name="packageship-panel",
    version="1.0",
    packages=find_packages(),
    requires=[
        "packageship",
        "aiohttp(==3.8.1)",
        "APScheduler(==3.8.1)",
        "lxml(==4.6.3)",
    ],
    license="The software package builds the data panel",
    author="gongzhengtang",
    data_files=[
        ("/usr/bin", ["pkgship-paneld", "pkgship-panel"]),
        ("/lib/systemd/system/", ["pkgship-panel.service"]),
        (
            "/etc/pkgship/",
            ["timed_task.yaml"],
        ),
        (
            os.path.join(get_python_lib(), "packageship_panel", "application", "core"),
            ["packageship_panel/application/core/obs_info_template.csv"],
        ),
    ],
    zip_safe=False,
)
