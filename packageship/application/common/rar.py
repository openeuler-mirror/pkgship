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


class Unpack:

    @classmethod
    def dispatch(cls, extend, *args, **kwargs):
        """
        diff decompression funcs are called by mapping
        :param extend: suffix（compression method）
        :param kwargs.file_path: compression files path
        :param kwargs.save_file: decompress files path
        """
        pass

    def bz2(self):
        """
        bz2
        """
        pass

    def gz(self):
        """
        gz
        """
        pass

    def tar(self):
        """
        tar
        """
        pass

    def zip(self):
        """
        zip
        """
        pass

    def xz(self):
        """
        xz
        """
        pass
