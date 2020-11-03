#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
TestInstallDepend
"""
import unittest
import json

from test.base_code.read_data_base import ReadTestBase
from packageship.application.apps.package.function.constants import ResponseCode


class TestInstallDepend(ReadTestBase):
    """
    TestInstallDepend
    """
    REQUESTS_KWARGS = {
        "url": "/packages/findInstallDepend",
        "method": "POST",
        "data": "",
        "content_type": "application/json"
    }

    def test_not_found_database_info_response(self):
        """
        Initialization failed. No database was generated. Database information could not be found
        Returns:
        """
        self.REQUESTS_KWARGS["data"] = json.dumps({"binaryName": "A1"})

        self.without_dbs_folder(self.REQUESTS_KWARGS, met=self, code=ResponseCode.NOT_FOUND_DATABASE_INFO)
        self.when_db_no_content(self.REQUESTS_KWARGS, met=self, code=ResponseCode.NOT_FOUND_DATABASE_INFO)

    def test_param_error_response(self):
        """
        test_empty_binaryName_dbList
        Returns:

        """
        param_error_list = [
            "{}",
            json.dumps({"binaryName": ""}),
            json.dumps({"binaryName": "dsd" * 200}),
            json.dumps({"binaryName": 0}),
            json.dumps({"binaryName": "CUnit",
                        "db_list": [12, 3, 4]}),
            json.dumps({"binaryName": "CUnit",
                        "db_list": "xxxxx"}),
        ]

        for error_param in param_error_list:
            self.REQUESTS_KWARGS["data"] = error_param

            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_pkg_name_not_found_response(self):
        """
        The package name is not in the database
        Returns:

        """
        self.REQUESTS_KWARGS["data"] = json.dumps({"binaryName": "qitiandasheng"})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)

        self.response_json_error_judge(resp_dict, resp_code=ResponseCode.PACK_NAME_NOT_FOUND, method=self)

    def test_db_name_error_response(self):
        """
        Database name error
        Returns:

        """
        self.REQUESTS_KWARGS["data"] = json.dumps({"binaryName": "CUnit",
                                                   "db_list": ["shifu", "bajie"]
                                                   })

        resp_dict = self.client_request(**self.REQUESTS_KWARGS)

        self.response_json_error_judge(resp_dict, resp_code=ResponseCode.DB_NAME_ERROR, method=self)

    def test_true_params_result(self):
        """
        test_true_params_result
        Returns:

        """
        self.compare_resp_and_output("install_depend", met=self)


if __name__ == '__main__':
    unittest.main()
