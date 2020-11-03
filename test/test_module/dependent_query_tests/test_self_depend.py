#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
TestSelfDepend
"""
import unittest
import json


from test.base_code.read_data_base import ReadTestBase
from packageship.application.apps.package.function.constants import ResponseCode


class TestSelfDepend(ReadTestBase):
    """
    TestSelfDepend
    """
    REQUESTS_KWARGS = {
        "url": "/packages/findSelfDepend",
        "method": "POST",
        "data": "",
        "content_type": "application/json"
    }

    def test_not_found_database_info_response(self):
        """
        Initialization failed. No database was generated. Database information could not be found
        Returns:

        """
        self.REQUESTS_KWARGS["data"] = json.dumps({"packagename": "A1"})

        self.without_dbs_folder(
            self.REQUESTS_KWARGS,
            met=self,
            code=ResponseCode.NOT_FOUND_DATABASE_INFO)

        self.when_db_no_content(
            self.REQUESTS_KWARGS,
            met=self,
            code=ResponseCode.NOT_FOUND_DATABASE_INFO)

    def test_param_error_response(self):
        """
        test_empty_binaryName_dbList
        Returns:

        """
        param_error_list = [
            "{}",
            json.dumps({"packagename": ""}),
            json.dumps({"packagename": "dsd" * 100}),
            json.dumps({"packagename": 0}),

            json.dumps({"packagename": "CUnit",
                        "selfbuild": 1}),
            json.dumps({"packagename": "CUnit",
                        "selfbuild": '3'}),
            json.dumps({"packagename": "CUnit",
                        "selfbuild": "3",
                        "withsubpack":"test"}),
            json.dumps({"packagename": "CUnit",
                        "selfbuild": "3",
                        "packtype": "test"}),
            json.dumps({"packagename": "CUnit",
                        "db_list": [12, 3, 4]}),
        ]

        for error_param in param_error_list:
            self.REQUESTS_KWARGS["data"] = error_param

            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(
                resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_pkg_name_not_found_response(self):
        """
        The package name is not in the database
        Returns:

        """
        self.REQUESTS_KWARGS["data"] = json.dumps(
            {"packagename": "qitiandasheng"})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)

        self.response_json_error_judge(
            resp_dict,
            resp_code=ResponseCode.PACK_NAME_NOT_FOUND,
            method=self)

    def test_db_name_error_response(self):
        """
        Database name error
        Returns:

        """
        self.REQUESTS_KWARGS["data"] = json.dumps(
            {"packagename": "CUnit", "db_list": ["shifu", "bajie"]})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict, resp_code=ResponseCode.DB_NAME_ERROR, method=self)

    def test_true_params_result(self):
        """
        test_true_params_result
        Returns:

        """
        self.compare_resp_and_output("self_depend", met=self)


if __name__ == '__main__':
    unittest.main()
