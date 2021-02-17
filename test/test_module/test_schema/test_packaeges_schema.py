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
TestPackSchema
"""

import unittest
import copy
from packageship.application.serialize.package import PackageSchema, SingleSchema
from packageship.application.serialize.validate import validate


class TestPackSchema(unittest.TestCase):
    """
    Test validator
    """
    parameters = {
        "database_name": "",
        "page_num": "",
        "page_size": "",
        "query_pkg_name": ""
    }

    def validate_parameters(self, key=None, value=None):
        """
        Copy the new dictionary validation to return the validation result
        Args:
            key: A key in a dictionary
            value: Values in the dictionary

        Returns:
            errors: The verification results
        """
        new_parameters = copy.deepcopy(self.parameters)
        new_parameters[key] = value
        result, errors = validate(PackageSchema, new_parameters)
        return errors

    def test_packages_schema_wrong(self):
        """
        Data validator, data type, and data range for all packages
        """
        errors = self.validate_parameters()
        self.assertNotEqual(errors, {})
        errors = self.validate_parameters("table_name", ['a'])
        self.assertNotEqual(errors, {})
        errors = self.validate_parameters("table_name", 1)
        self.assertNotEqual(errors, {})
        errors = self.validate_parameters("page_num", "a")
        self.assertNotEqual(errors, {})
        errors = self.validate_parameters("page_num", -1)
        self.assertNotEqual(errors, {})
        errors = self.validate_parameters("page_size", -1)
        self.assertNotEqual(errors, {})
        errors = self.validate_parameters("page_size", 201)
        self.assertNotEqual(errors, {})
        errors = self.validate_parameters("query_pkg_name", 1)
        self.assertNotEqual(errors, {})

    def test_packages_not_dict(self):
        """
        The data type of the test transfer is not a dictionary
        """
        new_list = []
        with self.assertRaises(TypeError):
            validate(PackageSchema, new_list)
        new_str = ""
        with self.assertRaises(TypeError):
            validate(PackageSchema, new_str)

    def test_single_error(self):
        """
        Test a single package validator, missing a required pass parameter
        """
        parameters_one = {
            "database_name": 1,
            "pkg_name": 1
        }
        result, errors = validate(SingleSchema, parameters_one)
        self.assertIsNotNone(result)
        self.assertNotEqual(errors, {})
        parameters_two = {
            "database_name": "a",
            "pkg_name": ""
        }
        result, errors = validate(SingleSchema, parameters_two)
        self.assertNotEqual(errors, {})
        parameters_three = {
            "database_name": "",
            "pkg_name": "a"
        }
        result, errors = validate(SingleSchema, parameters_three)
        self.assertIsNotNone(result)
        self.assertNotEqual(errors, {})

    def test_database_name_error(self):
        """
        The transmitted database name is not in the system
        """
        parameters_one = {
            "database_name": "c",
            "pkg_name": "a"
        }
        result, errors = validate(SingleSchema, parameters_one)
        self.assertIsNotNone(result)
        self.assertNotEqual(errors, {})
