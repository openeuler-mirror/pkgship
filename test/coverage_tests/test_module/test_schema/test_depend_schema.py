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
"""
TestDependSchema
"""
import unittest
from packageship.application.serialize.dependinfo import DependSchema, DownSchema
from packageship.application.serialize.validate import validate


class TestDependSchema(unittest.TestCase):
    """
    Test the dependInfo validator
    """

    def test_data_type_error(self):
        """
        Incorrect data type, or out of range
        """
        parameter = {
            "packagename": "",
            "depend_type": "",
            "parameter": {
                "db_priority": [""],
                "packtype": "",
                "with_subpack": "",
                "search_type": ""
            }
        }
        result, error = validate(DependSchema, parameter)
        self.assertNotEqual({}, error)
        self.assertIsNotNone(result)
        parameter = {
            "packagename": "a",
            "depend_type": "a"}
        result, error = validate(DependSchema, parameter)
        self.assertIsNotNone(result)
        self.assertNotEqual({}, error)
        parameter = {
            "packagename": "a",
            "depend_type": "a",
            "parameter": {"with_subpack": "dd"}}
        result, error = validate(DependSchema, parameter)
        self.assertIsNotNone(result)
        self.assertNotEqual({}, error)
        parameter = {
            "packagename": ["a"],
            "depend_type": ["installdep"]}
        result, error = validate(DependSchema, parameter)
        self.assertNotEqual({}, error)
        self.assertIsNotNone(result)
        parameter = {
            "packagename": ["a"],
            "depend_type": "installdep",
            "parameter": {
                "db_priority": ["a"],
                "packtype": "a"
            }
        }
        result, error = validate(DependSchema, parameter)
        self.assertIsNotNone(result)
        self.assertNotEqual({}, error)
        parameter = {
            "packagename": ["a"],
            "depend_type": "installdep",
            "parameter": {
                "db_priority": ["a"],
                "packtype": "a"
            }
        }
        result, error = validate(DependSchema, parameter, True)
        self.assertIsNotNone(result)
        self.assertNotEqual({}, error)

        parameter = {
            "packagename": ["a"],
            "depend_type": "bedep",
            "parameter": {
                "db_priority": "a",
                "packtype": "a"
            }
        }
        result, error = validate(DependSchema, parameter)
        self.assertIsNotNone(result)
        self.assertNotEqual({}, error)
        parameter = {
            "packagename": ["a"],
            "depend_type": "bedep"}
        result, error = validate(DependSchema, parameter)
        self.assertIsNotNone(result)
        self.assertNotEqual({}, error)
        parameter = {
            "packagename": ["a"],
            "depend_type": "bedep",
            "parameter": {
                "db_priority": ["test", "test"],
                "packtype": "source",
                "with_subpack": False,
                "search_type": "install"
            }
        }
        result, error = validate(DependSchema, parameter)
        self.assertIsNotNone(result)
        self.assertNotEqual({}, error)

    def test_bedepend(self):
        """
            Dependent databases are listed and there is only one,
            transmitted database name in the generated database
        """
        parameter = {
            "packagename": ["a"],
            "depend_type": "bedep",
            "parameter": {
                "db_priority": ["test", "test"],
                "with_subpack": False
            }
        }
        result, error = validate(DependSchema, parameter)
        self.assertIsNotNone(result)
        self.assertNotEqual({}, error)

        parameter = {
            "packagename": ["a"],
            "depend_type": "installdep",
            "parameter": {
                "db_priority": ["test"],
                "packtype": "source",
                "with_subpack": False,
                "search_type": "install"
            }
        }
        result, error = validate(DependSchema, parameter)
        self.assertIsNotNone(result)
        self.assertNotEqual({}, error)

    def test_download(self):
        """
            The database of the downloaded validator is a list and there is only one,
            the transmitted database name in the generated database
        """
        parameter = {
            "packagename": ["a"],
            "depend_type": "src",
            "parameter": {
                "db_priority": ["test"],
                "with_subpack": False
            }
        }
        result, error = validate(DownSchema, parameter)
        self.assertIsNotNone(result)
        self.assertNotEqual({}, error)
