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


class Download:

    def export(self, func_name, file_type="csv", **kwargs):
        """
            export cvs or excel files
            :param func_name: which types of function exported (packages, installdepend, builddepend,etc）
            :param file_type: exported files type, only support csv or excel
            :param kwargs: accessory functionality, such as binary streams or file paths
            :param kwargs.binary_stream: a binary streams would be exxported
            :param kwargs.save_path: exported path
            :param kwargs.temporary: temp files path
        """
        pass

    def _set_response_header(self, response, file):
        """
            :param response: response content
            :param file: file name
        """
        pass

    @property
    def response(self):
        """
            response body
        """
        pass
