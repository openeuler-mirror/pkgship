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


class TestQueryBinName(TestCase):
    query_package = QueryPackage(database_list=['openeuler', 'fedora'])

    def test_query_specify(self):
        """
        Test query specify binary package
        Returns:
        """
        self.query_package._db_session.query = MagicMock(return_value=MockData.read_mock_data('JudySource.json'))
        source_list = ['Judy']
        result = self.query_package.get_bin_name(source_list=source_list)
        expect_value = {'source_name': 'Judy',
                        'src_version': '1.0.5',
                        'database': 'openeuler',
                        'binary_infos': [{'bin_name': 'Judy', 'bin_version': '1.0.5'},
                                         {'bin_name': 'Judy-devel', 'bin_version': '1.0.5'},
                                         {'bin_name': 'Judy-help', 'bin_version': '1.0.5'}]
                        }

        self.assertEqual(result[0], expect_value)

    def test_src_list_empty(self):
        """
        Test input a empty binary packages list
        Returns:
        """
        source_list = []
        result = self.query_package.get_bin_name(source_list=source_list)

        self.assertListEqual(result, [])
