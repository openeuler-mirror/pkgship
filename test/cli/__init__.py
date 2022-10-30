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
test_pkgship_cmd
"""
import argparse
import os
import sys
from io import StringIO
import unittest
import json
import pathlib
from pathlib import Path
from unittest import mock
from flask.wrappers import Response
from packageship import BASE_PATH
from packageship.application.cli.base import BaseCommand

MOCK_DATA_FOLDER = str(Path(Path(__file__).parents[1], "mock_data"))
with open(str(Path(MOCK_DATA_FOLDER, "databaseinfo.json")), "r", encoding="utf-8") as f:
    DATA_BASE_INFO = json.loads(f.read())

ES_COUNT_DATA = {
    "count": 100,
    "_shards": {"total": 100, "successful": 1, "skipped": 0, "failed": 0},
}


class TestMixin:
    """
    Test Mixin class
    """

    def _es_search_result(self, index, body):
        """_es_search_result

        Args:
            index (str): query es index
            body (dict): query es body

        Raises:
            NotImplementedError:
        """
        raise NotImplementedError

    def _es_index_result(self, index, body, doc_type):
        """_es_index_result

        Args:
            index (str): query es index
            body (dict): query es body
            doc_type (str): doc type

        Raises:
            NotImplementedError:
        """
        raise NotImplementedError

    def _es_scan_result(self, client, index, query, scroll="3m", timeout="1m"):
        """_es_scan_result

        Args:
            client : es clinet
            index : query es index
            query : query es body
            scroll (str, optional):  Defaults to '3m'.
            timeout (str, optional):  Defaults to '1m'.

        Raises:
            NotImplementedError:
        """
        raise NotImplementedError

    def _es_count_result(self, index, body):
        """_es_count_result

        Args:
            index (str): query es index
            body (dict): query es body
            doc_type (str): doc type

        Raises:
            NotImplementedError:
        """
        raise NotImplementedError

    def _es_exists_result(self, index, id, doc_type=None):
        """_es_exists_result

        Args:
            index (str): The name of the index
            id ([type]): The document ID
            doc_type ([type], optional): The type of the document (use `_all` to fetch the
                first document matching the ID across all types). Defaults to None.
            params ([type], optional): [description]. Defaults to None.
            headers ([type], optional): [description]. Defaults to None.

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def _es_index_result(self, *args, **kwargs):
        """_es_index_result

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def _es_delete_result(self, *args, **kwargs):
        """_es_delete_result

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def _es_create_result(self, *args, **kwargs):
        """_es_create_result

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def _es_reindex_result(self, *args, **kwargs):
        """_es_reindex_result

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def _requests_get(self, *args, **kwargs):
        """_request_get"""
        raise NotImplementedError

    def _requests_post(self, *args, **kwargs):
        """_request_post"""
        raise NotImplementedError

    def _create_patch(self, mock_name, **kwargs):
        """create_patch

        Args:
            method_name (str): mock method or attribute name

        """
        patcher = mock.patch(mock_name, **kwargs)
        self._to_clean_mock_patchers.append(patcher)
        patcher.start()

    def _to_update_kw_and_make_mock(self, mock_name, effect=None, **kwargs):
        """_to_update_kw_and_make_mock

        Args:
            mock_name (str):  mock method or attribute name
            effect (Any, optional): side effect value

        Raises:
            ValueError: If the side_effect or return_value keyword parameter is not specified
                        specify the value of the effect keyword parameter
        """
        if "side_effect" not in kwargs and "return_value" not in kwargs:
            if effect is None:
                raise ValueError(
                    "If the side_effect or return_value keyword parameter is not specified,"
                    "specify the value of the effect keyword parameter"
                )
            kwargs["side_effect"] = effect
        self._create_patch(mock_name, **kwargs)

    def mock_es_scan(self, **kwargs):
        """mock_es_scan"""
        self._to_update_kw_and_make_mock(
            "elasticsearch.helpers.scan", effect=self._es_scan_result, **kwargs
        )

    def mock_es_search(self, **kwargs):
        """mock_es_search"""
        self._to_update_kw_and_make_mock(
            "elasticsearch.Elasticsearch.search",
            effect=self._es_search_result,
            **kwargs,
        )

    def mock_es_count(self, **kwargs):
        """mock_es_count"""
        self._to_update_kw_and_make_mock(
            "elasticsearch.Elasticsearch.count", effect=self._es_count_result, **kwargs
        )

    def mock_es_exists(self, **kwargs):
        """mock_es_exists"""

        self._to_update_kw_and_make_mock(
            "elasticsearch.client.indices.IndicesClient.exists",
            effect=self._es_exists_result,
            **kwargs,
        )

    def mock_es_delete(self, **kwargs):
        """mock elasticsearch delete"""
        self._to_update_kw_and_make_mock(
            "elasticsearch.client.indices.IndicesClient.delete",
            effect=self._es_delete_result,
            **kwargs,
        )

    def mock_es_insert(self, **kwargs):
        """mock_es_insert"""
        self._to_update_kw_and_make_mock(
            "elasticsearch.Elasticsearch.index", effect=self._es_index_result, **kwargs
        )

    def mock_es_create(self, **kwargs):
        """mock_es_create"""
        self._to_update_kw_and_make_mock(
            "elasticsearch.client.indices.IndicesClient.create",
            effect=self._es_create_result,
            **kwargs,
        )

    def mock_es_reindex(self, **kwargs):
        """mock_es_reindex"""
        self._to_update_kw_and_make_mock(
            "elasticsearch.Elasticsearch.reindex",
            effect=self._es_reindex_result,
            **kwargs,
        )

    def mock_requests_get(self, **kwargs):
        """mock_requests_get"""
        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.get",
            effect=self._requests_get,
            **kwargs,
        )

    def mock_requests_post(self, **kwargs):
        """mock_requests_post"""
        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.post",
            effect=self._requests_post,
            **kwargs,
        )

    @staticmethod
    def read_file_content(path, folder=MOCK_DATA_FOLDER, is_json=True):
        """to read file content if is_json is True return dict else return str

        Args:
            path: Absolute path or the path relative of mock_data folder
            is_json: if is True use json.loads to load data else not load

        Raises:
            FileNotFoundError:Check Your path Please
            JSONDecodeError:Check Your Josn flie Please

        Returns:
            file's content:if is_json is True return dict else return str
        """
        curr_path = Path(folder, path)
        if Path(path).is_absolute():
            curr_path = path

        with open(str(curr_path), "r", encoding="utf-8") as f_p:
            if is_json:
                return json.loads(f_p.read())
            else:
                return f_p.read()


class BaseTest(unittest.TestCase, TestMixin):
    """
    class for Test Base
    """

    cmd_class = None

    def setUp(self) -> None:
        """
        setUp Test Environment
        """
        self._to_clean_mock_patchers = []
        self.stdout_io = StringIO()
        self.excepted_str = ""
        self.command_params = []
        sys.stdout = sys.stderr = self.stdout_io

    def _execute_command(self):
        """
        To Simulated execution command line
        Returns:
            None
        """
        if self.cmd_class is None:
            raise ValueError(
                f"please check cmd_class variable in your {self},"
                f"assignment current do command class name"
            )

        ins = self.cmd_class()
        ins.register()
        args = ins.parse.parse_args(self.command_params)
        ins.do_command(args)

    @property
    def print_result(self):
        """
        execute cmd and return print redirect content
        Returns:
            print redirect result
        """
        self._execute_command()
        return self.stdout_io.getvalue().strip()

    def assert_result(self):
        """
        to assert command lines result as same sa excepted str
        Returns:
            None
        """
        self.assertEqual(
            self.excepted_str.strip().strip("\r\n").strip("\n"), self.print_result
        )

    def _to_add_cleanup(self):
        """_to_add_cleanup"""
        for tc in self._to_clean_mock_patchers:
            self.addCleanup(tc.stop)
        self._to_clean_mock_patchers.clear()

    def create_file(self, path, write_content=None):
        """Create a temporary file"""
        if not os.path.exists(path):
            try:
                os.makedirs(os.path.split(path)[0])
            except FileExistsError:
                pathlib.Path(path).touch()
        if write_content:
            with open(path, "w", encoding="utf-8") as file:
                file.write(write_content)
        return path

    def tearDown(self) -> None:
        """tearDown"""

        BaseCommand.parser = argparse.ArgumentParser(
            description="package related dependency management"
        )
        BaseCommand.subparsers = BaseCommand.parser.add_subparsers(
            help="package related dependency management"
        )
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self._to_add_cleanup()
        return super().tearDown()


class ClientTest(BaseTest):
    def setUp(self) -> None:
        """
        Client Test setup
        Set Environment variable "SETTINGS_FILE_PATH" to project pacjage.ini path
        """
        os.environ["SETTINGS_FILE_PATH"] = str(Path(BASE_PATH, "package.ini"))
        from packageship.application import init_app

        app = init_app("query")

        super(ClientTest, self).setUp()
        self.client = app.test_client()
        Response.text = Response.data
        Response.content = Response.data

    def tearDown(self) -> None:
        """
        to restore Environment variable "SETTINGS_FILE_PATH"

        Returns:
            None
        """
        os.environ["SETTINGS_FILE_PATH"] = "/etc/pkgship/package.ini"
        return super().tearDown()
