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
import os
import shutil
from packageship.application.query import database as db
from packageship.application.database.session import DatabaseSession
from packageship.libs.log import LOGGER
from .repo import RepoFile


def del_temporary_file(path, folder=False):
    """
    Description: Delete temporary files or folders

    Args:
        path: temporary files or folders
        folder: file or folder, fsiles are deleted by default
    """
    if not os.path.exists(path):
        return
    try:
        if folder:
            shutil.rmtree(path)
        else:
            os.remove(path)
    except IOError as error:
        LOGGER.error(error)


class ESJson(dict):
    """
    Encapsulation of a dictionary
    """

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        try:
            value = dict.__getitem__(self, key)
        except KeyError:
            value = ESJson()
            self.__setitem__(key, value)
        return value

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, key):
        return self.__getitem__(key)
