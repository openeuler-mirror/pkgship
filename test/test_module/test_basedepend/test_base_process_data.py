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
import unittest
from packageship.application.core.depend.basedepend import BaseDepend
from test.base_code.read_mock_data import MockData
from test.base_code.common_test_code import compare_two_values

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "data")

excepted_data = MockData.read_mock_json_data(
    os.path.join(MOCK_DATA_FILE, 'basedepend_data.json'))
if not excepted_data:
    raise ValueError("No mock Data")


class TestBaseDep(unittest.TestCase):

    ins = BaseDepend()
    ins.binary_dict, ins.source_dict = excepted_data.get('excepted_both_data')

    def test_depend_list(self):
        """ test_depend_list
            give binary_dict and source_dict values to see 
            if the depend_list method returns the expected value
        """
        res = self.ins.depend_list()
        self.assertTrue(
            compare_two_values(res, excepted_data.get('expected_depend_info')))

    def test_depend_filter_dict_error_param_root(self):
        """ test_depend_filter_dict_error_param_root
            error parameter 'root' given for filer dict method,
            excpetd raise valueerror
        """
        self.assertRaises(ValueError, self.ins.filter_dict, "qibajiushi", 1)

    def test_depend_filter_dict_error_param_level(self):
        """ test_depend_filter_dict_error_param_level
            error parameter 'level' given for filer dict method,
            excpetd raise valueerror
        """
        self.assertRaises(ValueError, self.ins.filter_dict, "A1", 0)

    def test_depend_filter_dict_error_param_direction(self):
        """ test_depend_filter_dict_error_param_direction
            error parameter 'direction' given for filer dict method,
            excpetd raise valueerror
        """
        self.assertRaises(ValueError,
                          self.ins.filter_dict,
                          "A1",
                          1,
                          direction="abc")

    def test_depend_filter_bothward_dict(self):
        """ test_depend_filter_bothward_dict
        give binary_dict and source_dict values to see
        if the filter_dict method with true parameter and direction is bothward 
        returns the expected value
        """
        res = self.ins.filter_dict("B1", level=2)
        self.assertTrue(
            compare_two_values(
                res, excepted_data.get('excepted_bothward_B1_level2')))

    def test_depend_filter_upward_dict(self):
        """test_depend_filter_upward_dict
        give binary_dict and source_dict values to see
        if the filter_dict method with true parameter and direction is upward 
        returns the expected value
        """
        res = self.ins.filter_dict("A1", level=2, direction="upward")
        self.assertTrue(
            compare_two_values(res,
                               excepted_data.get('excepted_upward_A1_level2')))

    def test_depend_filter_downward_dict(self):
        """test_depend_filter_downward_dict
        give binary_dict and source_dict values to see
        if the filter_dict method with true parameter and direction is upward 
        returns the expected value
        """
        res = self.ins.filter_dict("B1", level=2, direction="downward")
        self.assertTrue(
            compare_two_values(
                res, excepted_data.get('excepted_downward_B1_level2')))


if __name__ == "__main__":
    unittest.main()
