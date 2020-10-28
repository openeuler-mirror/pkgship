#!/usr/bin/python3
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

    def without_dbs_folder(self, request_args: dict, met=None, code=None):
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

            configuration.DATABASE_FOLDER_PATH = os.path.join(
                os.path.dirname(BASE_PATH), 'test', 'common_files', 'dbs')

    def when_db_no_content(self, request_args: dict, met=None, code=None):
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
            configuration.DATABASE_FOLDER_PATH = os.path.join(
                os.path.dirname(BASE_PATH), 'test', 'common_files', 'dbs')

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
