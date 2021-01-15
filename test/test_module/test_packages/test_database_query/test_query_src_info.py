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
from unittest import TestCase
from unittest.mock import MagicMock

from packageship.application.query.pkg import QueryPackage
from test.test_module.test_packages.mock_db_data import MockData


class TestQuerySourcePkgInfo(TestCase):
    query_package = QueryPackage()

    def test_query_specify(self):
        """
        Test query specify source package
        Returns:

        """
        self.query_package._db_session.query = MagicMock(return_value=MockData.read_mock_data("JudySource.json"))
        result = self.query_package.get_src_info(src_list=['Judy'], database='openeuler', page_num=1, page_size=20,
                                                 query_all=False)

        self.assertIsNotNone(result['data'][0]['Judy'])
