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
from copy import deepcopy
import unittest
from unittest import mock
from unittest.mock import MagicMock

from redis import Redis

from packageship.application.core.depend.be_depend import BeDepend
from packageship.application.query.pkg import QueryPackage
from packageship.application.query.depend import BeDependRequires
from packageship.application.common import constant
from test.base_code.read_mock_data import MockData
from test.base_code.common_test_code import compare_two_values

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "data")

excepted_data = MockData.read_mock_json_data(
    os.path.join(MOCK_DATA_FILE, 'bedepend_data.json'))
if not excepted_data:
    raise ValueError("No mock Data")


class TestBedep(unittest.TestCase):
    """test bedepend class
    """
    param = excepted_data.get('param')
    be_dep_data = excepted_data.get('be_dep_data')

    def test_get_subpacks_method_return_empty(self):
        """ test_get_subpacks_method_return_empty
            method get_src_info return data is empty list
        """
        local_param = deepcopy(self.param)
        local_param["parameter"]["packtype"] = "source"

        QueryPackage.get_src_info = MagicMock(return_value={"data": []})
        b = BeDepend(**local_param)
        b.be_depend()
        self.assertEqual(b.binary_dict, {})
        self.assertEqual(b.source_dict, {})

    def test_get_subpacks_return_empty_subpacks(self):
        """test_get_subpacks_return_empty_subpacks
           package not have subpacks 
        """
        local_param = deepcopy(self.param)
        local_param["parameter"]["packtype"] = "source"
        QueryPackage.get_src_info = MagicMock(
            return_value={"data": [{
                "Judy": {
                    "subpacks": []
                }
            }]})
        b = BeDepend(**local_param)
        b.be_depend()
        self.assertEqual(b.binary_dict, {})
        self.assertEqual(b.source_dict, {})

    def test_query_depend_empty_return(self):
        """ test_query_depend_empty_return]
            method query package be requires return empty list
        """
        BeDependRequires.get_be_req = MagicMock(return_value=[])
        b = BeDepend(**self.param)
        b.be_depend()
        self.assertEqual(b.source_dict, {})
        self.assertEqual(b.binary_dict, {})

    def test_install_query_depend(self):
        """ test_install_query_depend
        """
        BeDependRequires.get_be_req = MagicMock(
            return_value=excepted_data.get('be_dep_data'))
        QueryPackage.get_src_info = MagicMock(
            return_value={"data": [{
                "Judy": {
                    "subpacks": ["Judy-devel"]
                }
            }]})
        params = deepcopy(self.param)
        params["parameter"]["with_subpack"] = True
        b = BeDepend(**params)
        b.binary_dict = {
            'B1': {
                'database': 'Mainline',
                'install': ['ADY'],
                'name': 'B1',
                'source_name': 'B',
                'version': '1.1'
            }
        }
        b.be_depend()
        self.assertTrue(
            compare_two_values(b.binary_dict,
                               excepted_data.get('excepted_install_data')))

    def test_source_query_depend(self):
        """ test_source_query_depend
            parameter search_type is source
        """
        source_param = deepcopy(self.param)
        source_param["parameter"]["search_type"] = "source"
        BeDependRequires.get_be_req = MagicMock(return_value=self.be_dep_data)
        QueryPackage.get_src_info = MagicMock(return_value={"data": {}})
        b = BeDepend(**source_param)
        b.source_dict = {
            'T': {
                'database': 'Mainline',
                'build': ['ADY'],
                'name': 'B1',
                'source_name': 'B',
                'version': '1.1'
            }
        }
        b.be_depend()
        self.assertTrue(
            compare_two_values(b.source_dict,
                               excepted_data.get('excepted_source_dict')))

    def test_both_query_depend(self):
        """test_both_query_depend is both
        """
        both_param = deepcopy(self.param)
        del both_param["parameter"]["search_type"]
        BeDependRequires.get_be_req = MagicMock(return_value=self.be_dep_data)
        QueryPackage.get_src_info = MagicMock(return_value={"data": {}})
        b = BeDepend(**both_param)
        b.be_depend()
        self.assertTrue(
            compare_two_values([b.binary_dict, b.source_dict],
                               excepted_data.get('excepted_both_data')))

    def test_be_depend_dict(self):
        """ test_be_depend_dict method
            give binary_dict and source_dict values to see 
            if the bedepend_dict method returns the expected value
        """
        both_param = deepcopy(self.param)
        del both_param["parameter"]["search_type"]
        BeDependRequires.get_be_req = MagicMock(return_value=self.be_dep_data)
        QueryPackage.get_src_info = MagicMock(return_value={"data": {}})
        b = BeDepend(**both_param)
        b.be_depend()
        binary_dict, source_dict = b.depend_dict
        self.assertTrue(
            compare_two_values([binary_dict, source_dict],
                               excepted_data.get('excepted_both_data')))

    def test_bedepend_dict(self):
        """ test_bedepend_dict method
            give binary_dict and source_dict values to see 
            if the depend_dict method returns the expected value
        """
        both_param = deepcopy(self.param)
        del both_param["parameter"]["search_type"]
        BeDependRequires.get_be_req = MagicMock(return_value=self.be_dep_data)
        QueryPackage.get_src_info = MagicMock(
            return_value={"data": [{
                "Judy": {
                    "subpacks": ["Judy-devel"]
                }
            }]})
        b = BeDepend(**both_param)
        b.binary_dict, b.source_dict = excepted_data.get('binary_source_dict')
        beped_dict = b.bedepend_dict
        self.assertTrue(
            compare_two_values(beped_dict,
                               excepted_data.get('excepted_bedepend_dict')))

    @mock.patch.object(Redis, "exists")
    def test_call_func_with_true_param(self, mock_exists):
        """ test call function with mock redis exists method
        
        Args:
            mock_exists ([type]): [redis exists metho mock return value]
        """
        mock_exists.side_effect = [
            False,
            False,
            False,
            False,
        ]

        both_param = deepcopy(self.param)
        del both_param["parameter"]["search_type"]
        BeDependRequires.get_be_req = MagicMock(return_value=self.be_dep_data)
        QueryPackage.get_src_info = MagicMock(return_value={"data": {}})
        be_dep = BeDepend(**both_param)
        be_dep(**both_param)
        self.assertTrue(
            compare_two_values([be_dep.binary_dict, be_dep.source_dict],
                               excepted_data.get('excepted_both_data')))


if __name__ == "__main__":
    unittest.main()