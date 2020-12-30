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
from .depend import BaseDepend


class InstallDepend(BaseDepend):

    @property
    def depend_dict(self):
        """
            get the forward direction relationship with dict format
        """
        pass

    @property
    def bedepend_dict(self):
        """
            get the reverse direction relationship with dict format
        """
        pass

    def install_depend(self):
        """
            get binary rpm package(s) install depend relation
            :param bin_name: the list of package names needed to be searched
            :param db_priority: database name list
            :param level: The number of levels of dependency querying
       """
        pass

    def __call__(self, **kwargs):
        pass
