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
A way to compare the request mode and the correct result in a unit test
"""
import unittest
import os
import json
import shutil

from test.base_code.common_test_code import compare_two_values
from test.base_code.common_test_code import get_correct_json_by_filename
from packageship.libs.exception import Error
from packageship import BASE_PATH
from packageship.libs.conf import configuration


class TestBase(unittest.TestCase):
    """
        unittest unit test basic class
    """

    def client_request(
            self,
            url=None,
            method="GET",
            data=None,
            content_type=None):
        """
            Simulate client sending request
        """
        self.assertIsNotNone(url, msg="Error url")
        methods = {
            "GET", "POST", "PUT", "DELETE", "OPTIONS",
            "get", "post", "put", "delete", "options"
        }
        self.assertIn(method, methods, msg="Wrong way of requesting method")

        response = self.client.__getattribute__(
            method.lower())(url, data=data, content_type=content_type)
        response_content = json.loads(response.data)
        return response_content

    def response_json_format(self, response):
        """
            Json data judgment of corresponding content
        """
        self.assertIn("code", response, msg="Error in data format return")
        self.assertIn("msg", response, msg="Error in data format return")
        self.assertIn("data", response, msg="Error in data format return")

    def response_json_error_judge(self, resp, resp_code, method):
        """
        Method of comparison of correct results
        """
        from packageship.application.apps.package.function.constants import ResponseCode

        common_string = f"\nMethod:{method},\nparams:{method.REQUESTS_KWARGS}"

        self.assertIn("code", resp,
                      msg=f"Error in data format return ")
        self.assertEqual(resp_code,
                         resp.get("code"),
                         msg=f"Error in status code return {common_string}")

        self.assertIn("msg", resp, msg="Error in data format return")
        self.assertEqual(ResponseCode.CODE_MSG_MAP.get(resp_code),
                         resp.get("msg"),
                         msg=f"Error in status prompt return {common_string}")

        self.assertIn("data", resp,
                      msg=f"Error in data format return {common_string}")
        self.assertIsNone(resp.get("data"),
                          msg=f"Error in data format return {common_string}")

    def without_dbs_folder(self, request_args: dict, met=None, code=None, test_type=None):
        """
        Method of comparison of correct results
        """
        try:
            configuration.DATABASE_FOLDER_PATH = os.path.join(
                os.path.dirname(BASE_PATH), 'test', 'common_files', 'dbs', 'temp_dbs')

            resp_dict = self.client_request(**request_args)

            self.response_json_error_judge(
                resp_dict, resp_code=code, method=met)
        except Error:
            print("without_dbs_folder")
        finally:
            if os.path.exists(configuration.DATABASE_FOLDER_PATH):
                shutil.rmtree(configuration.DATABASE_FOLDER_PATH)

            if not test_type:
                dbs_folder = "dbs"
            else:
                dbs_folder = "operate_dbs"
            configuration.DATABASE_FOLDER_PATH = os.path.join(os.path.dirname(BASE_PATH),
                                                              'test',
                                                              'common_files',
                                                              dbs_folder)

    def when_db_no_content(self, request_args: dict, met=None, code=None, test_type=None):
        """
        When there is no database, expectations are compared to actual results
        """
        try:
            from packageship.application.apps.package.function.constants import ResponseCode

            configuration.DATABASE_FOLDER_PATH = os.path.join(
                os.path.dirname(BASE_PATH), 'test', 'common_files', 'empty_dbs')

            resp_dict = self.client_request(**request_args)

            self.response_json_error_judge(
                resp_dict, resp_code=code, method=met)

        except Error:
            print("when_db_no_content")
        finally:
            if not test_type:
                dbs_folder = "dbs"
            else:
                dbs_folder = "operate_dbs"
            configuration.DATABASE_FOLDER_PATH = os.path.join(os.path.dirname(BASE_PATH),
                                                              'test',
                                                              'common_files',
                                                              dbs_folder)

    def compare_resp_and_output(self, file_name, met=None):
        """
        Dependent output, expected versus actual results
        """
        correct_list = get_correct_json_by_filename(file_name)

        self.assertNotEqual(
            [],
            correct_list,
            msg=f"Error reading JSON file name {file_name}")

        for correct_data in correct_list:
            input_value = correct_data["input"]
            met.REQUESTS_KWARGS["data"] = json.dumps(input_value)

            resp_dict = self.client_request(**met.REQUESTS_KWARGS)
            output_for_input = correct_data["output"]

            self.assertTrue(
                compare_two_values(
                    output_for_input,
                    resp_dict),
                msg=f"The answer is not correct \n Method:{met},Params:{met.REQUESTS_KWARGS}")

    def compare_response_get_out(self, file_name, resp_dict):
        """
        A comparison between the output and the actual result
        """
        correct_list = get_correct_json_by_filename(file_name)
        self.assertNotEqual(
            [],
            correct_list,
            msg=f"Error reading JSON file name {file_name}")
        self.assertIn("code", resp_dict, msg="Error in data format return")
        self.assertIn("data", resp_dict, msg="Error in data format return")
        self.assertIn("msg", resp_dict, msg="Error in data format return")
        self.assertTrue(
            compare_two_values(
                resp_dict.get("data"),
                correct_list),
            msg="Error in data information return")

    def find_all_py_file(self, path_list, file_list=[]):
        directory_list = []
        for file_path in path_list:
            for file in os.listdir(file_path):
                f_path = file_path + '/' + file
                if os.path.isdir(f_path):
                    directory_list.append(f_path)
                elif ".py" in f_path and ".pyc" not in f_path:
                    file_list.append(f_path)
        if directory_list:
            self.find_all_py_file(directory_list)
        else:
            self.check_licence(file_list)


    def check_licence(self, file_list):
        results_list = []
        str = "# See the Mulan PSL v2 for more details."
        for file in file_list:
            rec = open(file, 'r+', encoding="utf-8")
            line_Infos = rec.readlines()
            resultFlag = False
            for row in line_Infos:
                if row.strip().find(str) != -1:
                    resultFlag = True
                    break
            if resultFlag == False:
                results_list.append(file)
            rec.close()
        if len(results_list) != 0:
            print("licence error please add The following files licence", results_list)
        self.assertEqual(0, len(results_list),
                         msg=f"The licence is not complete, please add")
