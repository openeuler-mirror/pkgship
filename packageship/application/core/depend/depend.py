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
# from .install_depend import InstallDepend


class DispatchDepend:
    """
        Factory method, distributing operations of different depend search
    """
    def __init__(self, depend):
        self._depend = depend

    def execute(self, **kwargs):
        self._depend()


class BaseDepend:

    def depend_list(self):
        """
            get the depend relationship with list format
        """
        pass

    def download_depend_files(self):
        """
            get the depend relationship with downloadable files
        """
        pass

    def depend_info_graph(self):
        """
            get the depend relationship with graph format
        """
        pass

class DataProcess:

    def reverse(self):
        """
            reverse dict
        """
        pass

    def filter_dict(self, root, level):
        pass

    def depend_lines(self):
        pass
