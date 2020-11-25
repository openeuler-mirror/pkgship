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
"""
test save sig info in database
"""
import datetime
import os
import shutil
import time
import unittest
import warnings
from configparser import ConfigParser
from datetime import datetime
from test.base_code.operate_data_base import OperateTestBase
import yaml
from requests import HTTPError, RequestException

from packageship.libs.conf import configuration
from packageship.selfpkg import app

from packageship.application.apps.package.function.add_sig_info import SigInfo
from packageship.application.models.package import PackagesMaintainer
from packageship.libs.dbutils import DBHelper
from packageship.libs.exception import Error
from packageship.system_config import BASE_PATH


class TestSigInfo(OperateTestBase):
    """
    class for test save sig info
    """
    def setUp(self):

        warnings.filterwarnings("ignore")

    def __delete_packages_maintainer_info(self):
        with DBHelper(db_name='lifecycle') as data_name:
            data_name.session.query(PackagesMaintainer.sig).filter().delete()
            data_name.session.commit()

    def test_not_found_database_info_response(self):
        """test if initialization fails"""
        try:
            configuration.DATABASE_FOLDER_PATH = os.path.join(
                os.path.dirname(BASE_PATH), 'test', 'common_files', 'temp_dbs')
            sig_info = SigInfo()
            app.apscheduler.add_job(func=sig_info.save_all_packages_sigs_data, trigger='date',
                                    next_run_time=datetime.now(), id='save_sigs_data_1')
        except Error:
            raise AssertionError("the test of not found database info response failed")

        finally:
            configuration.DATABASE_FOLDER_PATH = os.path.join(
                os.path.dirname(BASE_PATH), 'test', 'common_files', 'operate_dbs')

    def test_trigger_scheduled_task(self):
        """Test whether the timing task can be triggered successfully
        and whether the sig information can be inserted successfully"""

        try:
            self.__delete_packages_maintainer_info()
            sig_info = SigInfo()
            app.apscheduler.add_job(func=sig_info.save_all_packages_sigs_data, trigger='date',
                                    next_run_time=datetime.now(), id='save_sigs_data_2')
            time.sleep(10)

            with DBHelper(db_name='lifecycle') as data_name:
                sig_list = data_name.session.query(
                    PackagesMaintainer.sig).all()

            self.assertNotEqual([],
                                sig_list,
                                msg="Error in insert or update sig info")
            self.__delete_packages_maintainer_info()

        except Error:
            raise AssertionError("the test of trigger scheduled task failed")

    def test_wrong_sig_url(self):
        """test if getting the wrong url"""
        sys_path = os.environ.get('SETTINGS_FILE_PATH')
        try:

            if os.path.exists(sys_path):
                shutil.copyfile(sys_path, sys_path + '.bak')
            self.__delete_packages_maintainer_info()
            config = ConfigParser()
            config.read(sys_path)
            config.set("SYSTEM", "sig_url", "www.baidu.com")
            config.write(open(sys_path, "w"))
            sig_info = SigInfo()
            app.apscheduler.add_job(func=sig_info.save_all_packages_sigs_data, trigger='date',
                                    next_run_time=datetime.now(), id='save_sigs_data_3')

            with DBHelper(db_name='lifecycle') as data_name:
                sig_list = data_name.session.query(
                    PackagesMaintainer.sig).all()

            self.assertEqual([], sig_list, msg="An abnormal error occurred while "
                                               "reading sig content from yaml file")

        except (yaml.YAMLError, FileNotFoundError, HTTPError, Error, RequestException):
            raise AssertionError("the test of wrong sig url failed")

        finally:
            if os.path.exists(sys_path) and os.path.exists(sys_path + '.bak'):
                os.remove(sys_path)
                os.rename(sys_path + '.bak', sys_path)


if __name__ == '__main__':
    unittest.main()