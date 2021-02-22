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
Logging related
"""
import os
import pathlib
import logging
from .conf import configuration


class Log():
    """
        operation log of the system
    """

    def __init__(self, name=__name__, path=None):
        self.__file_handler = None

        self.__path = os.path.join(
            configuration.LOG_PATH, configuration.LOG_NAME)
        if path:
            self.__path = path

        if not os.path.exists(self.__path):
            try:
                os.makedirs(os.path.split(self.__path)[0])
            except FileExistsError:
                pathlib.Path(self.__path).touch()

        self.__level = configuration.LOG_LEVEL
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(self.__level)

    def __init_handler(self):
        self.__file_handler = logging.FileHandler(
            self.__path, encoding="utf-8")

        self.__set_handler()
        self.__set_formatter()

    def __set_handler(self):
        self.__file_handler.setLevel(self.__level)
        self.__logger.addHandler(self.__file_handler)

    def __set_formatter(self):
        formatter = logging.Formatter('%(asctime)s-%(name)s-%(filename)s-[line:%(lineno)d]'
                                      '-%(levelname)s-[ log details ]: %(message)s',
                                      datefmt='%a, %d %b %Y %H:%M:%S')
        self.__file_handler.setFormatter(formatter)

    @property
    def logger(self):
        """
            Gets the logger property
        """
        if not self.__file_handler:
            self.__init_handler()
        return self.__logger

    @property
    def file_handler(self):
        """
        The file handle to the log
        """
        if not self.__file_handler:
            self.__init_handler()
        return self.__file_handler


LOGGER = Log(__name__).logger
