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


class Package:

    def all_src_packages(self):
        """
            get all source rpm packages base info
        """
        pass

    def all_bin_packages(self):
        """
            get all binary rpm packages base info
        """
        pass

class SourcePackage:

    def src_package_info(self):
        """
            get a source package info (provides, requires, etc)
        """
        pass


class BinaryPackage:

    def bin_package_info(self):
        """
            get a binary package info (provides, requires, etc)
        """
        pass
