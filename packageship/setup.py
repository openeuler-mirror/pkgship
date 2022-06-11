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

_CONFIG_PATH = "/etc/pkgship/"
PACKAGE_PATH = get_python_lib()
MAPPING_PATH = os.path.join(PACKAGE_PATH, "packageship", "application", "common", "rsp")
PACKAGESHIP_PATH = os.path.join(PACKAGE_PATH, "packageship")

INITIALIZE_PATH = os.path.join(
    PACKAGE_PATH, "packageship", "application", "initialize", "mappings"
)

setup(
    name="packageship",
    version="3.0.0",
    packages=find_packages(),
    requires=[
        "prettytable (==0.7.2)",
        "Flask_RESTful (==0.3.8)",
        "Flask_Script (==2.0.6)",
        "Flask (==1.1.2)",
        "marshmallow (==3.5.1)",
        "PyYAML (==5.3.1)",
        "requests (==2.21.0)",
        "uwsgi (==2.0.18)",
        "gevent(==20.12.1)",
        "Flask_Limiter(==1.4)",
        "elasticsearch(==7.10.1)",
        "redis(==3.5.3)",
        "retrying(==1.3.3)",
        "aiohttp(==3.8.1)",
        "APScheduler(==3.8.1)",
        "lxml(==4.6.3)",
    ],
    license="Dependency package management",
    author="wangyiru",
    data_files=[
        (
            _CONFIG_PATH,
            [
                "package.ini",
                "conf.yaml",
                "auto_install_pkgship_requires.sh",
                "uwsgi_logrotate.sh",
            ],
        ),
        ("/usr/bin", ["pkgshipd", "pkgship"]),
        ("/lib/systemd/system/", ["pkgship.service"]),
        (MAPPING_PATH, ["packageship/application/common/rsp/mapping.xml"]),
        (PACKAGESHIP_PATH, ["version.yaml"]),
        (
            INITIALIZE_PATH,
            [
                "packageship/application/initialize/mappings/bedepend.json",
                "packageship/application/initialize/mappings/binary.json",
                "packageship/application/initialize/mappings/source.json",
            ],
        ),
    ],
    zip_safe=False,
)
