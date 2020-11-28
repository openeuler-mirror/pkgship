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
test import_databases
"""
import os
import shutil
import unittest
import warnings
from configparser import ConfigParser

import yaml

from packageship import BASE_PATH
from packageship.libs.exception import ConfigurationException

try:
    os.environ["SETTINGS_FILE_PATH"] = os.path.join(os.path.dirname(BASE_PATH),
                                                    'test',
                                                    'common_files',
                                                    'package.ini')
    base_path = os.path.join(os.path.dirname(BASE_PATH),
                             "test",
                             "common_files")
    config = ConfigParser()
    sys_path = os.environ.get('SETTINGS_FILE_PATH')
    config.read(sys_path)
    conf_path = os.path.join(base_path, "conf.yaml")
    from test.base_code.init_config_path import init_config

except (FileNotFoundError, ValueError):
    raise FileNotFoundError


from packageship.application.initsystem.data_import import InitDataBase
from packageship.libs.exception import ContentNoneException
from packageship.libs.exception import DatabaseRepeatException
from packageship.application.models.package import DatabaseInfo
from packageship.libs.dbutils import DBHelper


class ImportData(unittest.TestCase):
    """
    test importdatabases
    """

    def setUp(self):
        warnings.filterwarnings("ignore")

    def write_data_in_yaml_method(self, test_data):
        """Write data in the YAML file"""

        try:
            if os.path.exists(conf_path):
                shutil.copyfile(conf_path, conf_path + ".bak")
            with open(conf_path, "w", encoding="utf-8") as w_f:
                yaml.dump(test_data, w_f)
            with self.assertRaises(ConfigurationException):
                InitDataBase(config_file_path=conf_path).init_data()
        except FileExistsError:
            print("The file already exists")
        finally:
            if os.path.exists(conf_path) and os.path.exists(
                    conf_path + ".bak"):
                os.remove(conf_path)
                os.rename(conf_path + ".bak", conf_path)

    def common_yaml_filed_raise_method(self, field, data, error):
        """
        Yaml single-field common methods
        Args:
            field: field
            data:  data
            error: error

        Returns:

        """
        try:
            if os.path.exists(conf_path):
                shutil.copyfile(conf_path, conf_path + ".bak")
            with open(conf_path, 'r', encoding='utf-8') as file:
                origin_yaml = yaml.load(file.read(), Loader=yaml.FullLoader)
                for obj in origin_yaml:
                    obj[field] = data
                with open(conf_path, 'w', encoding='utf-8') as w_f:
                    yaml.dump(origin_yaml, w_f)
            with self.assertRaises(error):
                InitDataBase(config_file_path=conf_path).init_data()
        except FileExistsError:
            print("An error occurred and the results were compared to an exception")
        finally:
            if os.path.exists(conf_path) and os.path.exists(
                    conf_path + ".bak"):
                os.remove(conf_path)
                os.rename(conf_path + ".bak", conf_path)

    def common_yaml_filed_bin_or_src(self, db_file, data, correct_list):
        """
        common_yaml_filed_bin_or_src
        Args:
            db_file: db_file
            data: data
            correct_list: correct_list

        Returns:

        """
        try:
            if os.path.exists(conf_path):
                shutil.copyfile(conf_path, conf_path + ".bak")
            with open(conf_path, 'r', encoding='utf-8') as file:
                origin_yaml = yaml.load(file.read(), Loader=yaml.FullLoader)
                for obj in origin_yaml:
                    obj[db_file] = data
                with open(conf_path, 'w', encoding='utf-8') as w_f:
                    yaml.dump(origin_yaml, w_f)
            InitDataBase(config_file_path=conf_path).init_data()
            with DBHelper(db_name='lifecycle') as data_name:
                name_list = data_name.session.query(
                    DatabaseInfo.name, DatabaseInfo.priority).order_by(DatabaseInfo.priority).all()
                data_list = [dict(zip(ven.keys(), ven)) for ven in name_list]
            self.assertEqual(
                data_list,
                correct_list,
                msg='error content not pattern')
        except FileExistsError:
            print("An error occurred and the results were compared to an exception")
        finally:
            if os.path.exists(conf_path) and os.path.exists(
                    conf_path + ".bak"):
                os.remove(conf_path)
                os.rename(conf_path + ".bak", conf_path)

    def test_yaml_address_none(self):
        """The initialization file address is None"""
        with self.assertRaises(ContentNoneException):
            InitDataBase(config_file_path=None).init_data()

    def test_wrong_yaml_path(self):
        """
        Test the packa.ini file init_conf_path parameter for error
        """
        try:
            if os.path.exists(sys_path):
                shutil.copyfile(sys_path, sys_path + ".bak")
            config_obj = ConfigParser()
            config_obj.read(sys_path)
            config_obj.set("SYSTEM", "init_conf_path", "/var/test/conf.yaml")
            config_obj.write(open(sys_path, "w"))
            new_conf_path = config_obj.get('SYSTEM', "init_conf_path")
            with self.assertRaises(FileNotFoundError) as meg:
                InitDataBase(config_file_path=new_conf_path).init_data()
            error_msg = "system initialization configuration filedoes not exist: {}".format(
                new_conf_path)
            self.assertEqual(error_msg, str(meg.exception),
                             msg='error content not pattern')
        except FileExistsError:
            print("An error occurred and the results were compared to an exception")
        finally:
            if os.path.exists(sys_path) and os.path.exists(sys_path + ".bak"):
                os.remove(sys_path)
                os.rename(sys_path + ".bak", sys_path)

    def test_format_conf_yaml(self):
        """
        Wrong YAML format
        """
        wrong_format_yaml_path = os.path.join(
            base_path, "wrong_format_conf.yaml")

        with self.assertRaises(ConfigurationException):
            InitDataBase(config_file_path=wrong_format_yaml_path).init_data()

    def test_yaml_format_list(self):
        """
        The format in YAML is not a list
        """
        test_data = {"androidProcess": "com.mm:tools"}
        self.write_data_in_yaml_method(test_data)

    def test_yaml_format_dict(self):
        """The format in YAML is not a nested list dictionary"""
        test_data = ['python', 'java', 'c++', 'C#',
                     {'androidProcess': 'com.mm:tools'}, ["python", "c++", "java"]]
        self.write_data_in_yaml_method(test_data)

    def test_yaml_content_empty(self):
        """The contents of YAML are empty"""
        try:
            shutil.copyfile(conf_path, conf_path + '.bak')
            with open(conf_path, 'w', encoding='utf-8') as w_f:
                w_f.write("")
            with self.assertRaises(ConfigurationException):
                InitDataBase(config_file_path=conf_path).init_data()
        except FileExistsError:
            print("An error occurred and the results were compared to an exception")
        finally:
            if os.path.exists(conf_path) and os.path.exists(
                    conf_path + ".bak"):
                os.remove(conf_path)
                os.rename(conf_path + '.bak', conf_path)

    def test_dbname_none(self):
        """dbname in the YAML file is none"""
        single_field = "dbname"
        data = ""
        error = DatabaseRepeatException
        self.common_yaml_filed_raise_method(single_field, data, error)

    def test_repeat_data_name(self):
        """Yaml file exists but DB exists_ The same with name"""
        single_field = "dbname"
        data = "openEuler"
        error = DatabaseRepeatException
        self.common_yaml_filed_raise_method(single_field, data, error)

    def test_yaml_bin_db_file_none(self):
        """Bin_db_file does not exist in YAML"""
        db_file = "bin_db_file"
        data = ""
        correct_list = list()
        self.common_yaml_filed_bin_or_src(db_file, data, correct_list)

    def test_yaml_src_db_file_none(self):
        """Bin_db_file does not exist in YAML"""
        db_file = "src_db_file"
        data = ""
        correct_list = list()
        self.common_yaml_filed_bin_or_src(db_file, data, correct_list)

    def test_yaml_priority(self):
        """Test priority in YAML"""
        db_file = "priority"
        data = "test"
        correct_list = list()
        self.common_yaml_filed_bin_or_src(db_file, data, correct_list)

    def test_yaml_priority_none(self):
        """Test priority is none in YAML """
        db_file = "priority"
        data = ""
        correct_list = list()
        self.common_yaml_filed_bin_or_src(db_file, data, correct_list)

    def test_yaml_priority_zero(self):
        """Test priority is none in YAML """

        db_file = "priority"
        data = "0"
        correct_list = list()
        self.common_yaml_filed_bin_or_src(db_file, data, correct_list)

    def test_yaml_priority_hundred(self):
        """Test priority is none in YAML """
        db_file = "priority"
        data = "101"
        correct_list = list()
        self.common_yaml_filed_bin_or_src(db_file, data, correct_list)

    def test_yaml_lifecycle_not(self):
        """Test priority in YAML"""
        db_file = "priority"
        data = "101"
        correct_list = list()
        self.common_yaml_filed_bin_or_src(db_file, data, correct_list)

    def test_yaml_lifecycle_enable(self):
        """test yaml """
        try:
            if os.path.exists(conf_path):
                shutil.copyfile(conf_path, conf_path + ".bak")
            shutil.copyfile(conf_path, conf_path + '.bak')
            with open(conf_path, 'r', encoding='utf-8') as file:
                origin_yaml = yaml.load(file.read(), Loader=yaml.FullLoader)
                for obj in origin_yaml:
                    obj["lifecycle"] = "disable"
                with open(conf_path, 'w', encoding='utf-8') as w_f:
                    yaml.dump(origin_yaml, w_f)
            InitDataBase(config_file_path=conf_path).init_data()
            with DBHelper(db_name='lifecycle') as data_name:
                name_list = data_name.session.query(
                    DatabaseInfo.name, DatabaseInfo.priority).order_by(DatabaseInfo.priority).all()
                data_list = [dict(zip(ven.keys(), ven)) for ven in name_list]
            with open(conf_path, 'r', encoding='utf-8') as file:
                origin_yaml = yaml.load(file.read(), Loader=yaml.FullLoader)
                origin_list = list()
                for item in origin_yaml:
                    data_dict = dict()
                    data_dict['name'] = item.get("dbname")
                    data_dict['priority'] = item.get("priority")
                    origin_list.append(data_dict)
            self.assertEqual(
                data_list,
                origin_list,
                msg='error content not pattern')
            with DBHelper(db_name='lifecycle') as data_name:
                table_list = data_name.engine.table_names()
                new_table_list = [
                    x for x in table_list if x not in [
                        "databases_info",
                        "packages_issue",
                        "packages_maintainer"]]
            self.assertEqual(
                new_table_list,
                [],
                msg='error content not pattern')
        except FileExistsError:
            print("An error occurred and the results were compared to an exception")
        finally:
            if os.path.exists(conf_path) and os.path.exists(
                    conf_path + ".bak"):
                os.remove(conf_path)
                os.rename(conf_path + '.bak', conf_path)

    def test_true_init(self):
        """test true yaml"""
        InitDataBase(config_file_path=conf_path).init_data()
        with DBHelper(db_name='lifecycle') as data_name:
            name_list = data_name.session.query(
                DatabaseInfo.name, DatabaseInfo.priority).order_by(DatabaseInfo.priority).all()
            data_list = [dict(zip(ven.keys(), ven)) for ven in name_list]
        with open(conf_path, 'r', encoding='utf-8') as file:
            origin_yaml = yaml.load(file.read(), Loader=yaml.FullLoader)
            origin_list = list()
            for item in origin_yaml:
                data_dict = dict()
                data_dict['name'] = item.get("dbname")
                data_dict['priority'] = item.get("priority")
                origin_list.append(data_dict)

        self.assertEqual(
            data_list,
            origin_list,
            msg="The name and priority of the data generated by the initialization are correct")

    def test_wrong_remote_address_src(self):
        """
        Src_db_file remote address error
        """
        db_file = "src_db_file"
        data = "www.baidu.com"
        correct_list = list()
        self.common_yaml_filed_bin_or_src(db_file, data, correct_list)

    def test_wrong_remote_address_bin(self):
        """
        Bin_db_file remote address error
        """
        db_file = "bin_db_file"
        data = "www.baidu.com"
        correct_list = list()
        self.common_yaml_filed_bin_or_src(db_file, data, correct_list)

    def test_true_remote_address(self):
        """
        The remote address parameter is correct
        """
        try:
            if os.path.exists(conf_path):
                shutil.copyfile(conf_path, conf_path + ".bak")
            with open(conf_path, 'r', encoding='utf-8') as file:
                origin_yaml = yaml.load(file.read(), Loader=yaml.FullLoader)
                origin_yaml[0]['src_db_file'] = \
                    "https://repo.openeuler.org/openEuler-20.03-LTS/source"
                origin_yaml[0]['bin_db_file'] = \
                    "https://repo.openeuler.org/openEuler-20.03-LTS/everything/aarch64"
                origin_yaml[1]['src_db_file'] = \
                    "https://repo.openeuler.org/openEuler-20.09/source"
                origin_yaml[1]['bin_db_file'] = \
                    "https://repo.openeuler.org/openEuler-20.09/everything/aarch64"
                with open(conf_path, 'w', encoding='utf-8') as w_f:
                    yaml.dump(origin_yaml, w_f)
            InitDataBase(config_file_path=conf_path).init_data()
            with DBHelper(db_name='lifecycle') as data_name:
                name_list = data_name.session.query(
                    DatabaseInfo.name, DatabaseInfo.priority).order_by(DatabaseInfo.priority).all()
                data_list = [dict(zip(ven.keys(), ven)) for ven in name_list]
            with open(conf_path, 'r', encoding='utf-8') as file:
                origin_yaml = yaml.load(file.read(), Loader=yaml.FullLoader)
                origin_list = list()
                for item in origin_yaml:
                    data_dict = dict()
                    data_dict['name'] = item.get("dbname")
                    data_dict['priority'] = item.get("priority")
                    origin_list.append(data_dict)
            self.assertEqual(
                data_list,
                origin_list,
                msg='error content not pattern')
        except FileExistsError:
            print("An error occurred and the results were compared to an exception")
        finally:
            if os.path.exists(conf_path) and os.path.exists(
                    conf_path + ".bak"):
                os.remove(conf_path)
                os.rename(conf_path + ".bak", conf_path)


if __name__ == '__main__':
    unittest.main()
