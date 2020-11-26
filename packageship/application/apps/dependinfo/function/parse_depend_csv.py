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
Process the restful interface response data as required and save it to the corresponding csv file
"""
from typing import List
from functools import wraps

from flask import current_app

from packageship.application.apps.package.function.constants import ListNode


def catch_error(func):
    """
    Exception capture decorator
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, TypeError, AttributeError, IndexError) as error:
            current_app.logger.error(error)
            raise ValueError("input json_data is error! please check")
        except IOError as io_error:
            current_app.logger.error(io_error)
            raise ValueError("There is an error in writing the file."
                             "Please confirm whether you have permission.")

    return inner


class BaseDep:
    """
    Basic methods for parsing data
    """

    def __init__(self):
        """
        Instantiate the underlying data structure
        """
        self.data = dict()
        self.install_dict = dict()
        self.build_dict = dict()

    @catch_error
    def _init_install_data(self, bin_name: str, lst: List):
        """
        init install dict data
        Args:
            bin_name:binary package name
            lst:csv row data

        Returns:

        """

        if bin_name not in self.install_dict:
            self.install_dict[bin_name] = {
                "source_name": lst[ListNode.SOURCE_NAME],
                "version": lst[ListNode.VERSION],
                "db_name": lst[ListNode.DBNAME],
                "install": []
            }

    @catch_error
    def _process_install_dict(self, bin_name, parent_name):
        """
        Parse the Install data type
        Args:
            bin_name: Binary package name
            parent_name: The name of the parent node package

        Returns:

        """
        if parent_name not in self.install_dict:
            self.install_dict[parent_name] = {
                "source_name": self.data.get(parent_name)[ListNode.SOURCE_NAME],
                "version": self.data.get(parent_name)[ListNode.VERSION],
                "db_name": self.data.get(parent_name)[ListNode.DBNAME],
                "install": [bin_name]}

        else:
            if bin_name not in self.install_dict[parent_name]["install"]:
                self.install_dict[parent_name]["install"].append(bin_name)
