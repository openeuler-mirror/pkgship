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
Description: get pkgship version
"""

import os
import yaml
from packageship import BASE_PATH
from packageship.libs.log import LOGGER
file_path = os.path.join(os.path.dirname(BASE_PATH), "packageship", "version.yaml")

def get_pkgship_version():
    """
    Get the version and release of pkgship

    Returns:
        version, release

    Attributes:
        yaml.YAMLError: read yaml file error
        FileNotFoundError: file not found
        KeyError: key not exists

    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file_context:
            yaml_content = yaml.load(file_context.read(), Loader=yaml.FullLoader)
        version = yaml_content["Version"]
        release = yaml_content["Release"]
        return version, release
    except (yaml.YAMLError, FileNotFoundError, KeyError) as e:
        LOGGER.error(e)
        return None, None
