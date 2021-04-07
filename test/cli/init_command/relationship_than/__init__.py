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
# -*- coding:utf-8 -*-
import os
from packageship.libs.conf import configuration
from packageship.application.initialize.integration import del_temporary_file


CONFIG_CONTENT = """
- dbname: openeuler
  src_db_file: {src}
  bin_db_file: {bin}
  priority: 1
"""


class RelationComparison():
    """
    Initializes a dependency result alignment
    """

    def prepare(self, test, dirname):
        """
        Construct the necessary conditions for comparison of results
        """
        path = os.path.join(dirname, "sqlites")
        _cofig_content = CONFIG_CONTENT.format(src="file://" + os.path.join(path, "src"),
                                               bin="file://" + os.path.join(path, "bin"))
        test._conf = test.create_conf_file(
            content=_cofig_content, path=test._create_file_path)
        configuration.TEMPORARY_DIRECTORY = os.path.join(dirname, "tmp")
        test.comparsion_than()

    def tear_down(self):
        """
        Conditions of reductive structure
        """
        folder = os.path.join(self._dirname, "conf")
        del_temporary_file(path=folder, folder=True)
        del_temporary_file(path=os.path.join(
            self._dirname, "tmp"), folder=True)
        configuration.TEMPORARY_DIRECTORY = "/opt/pkgship/tmp/"
