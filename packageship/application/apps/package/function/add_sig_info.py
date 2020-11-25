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
read yaml file, parse sig info, save sig info in database
"""
import os
import requests
import yaml
from retrying import retry
from sqlalchemy import literal_column
from sqlalchemy.exc import SQLAlchemyError
from requests.exceptions import HTTPError, RequestException
from packageship.libs.log import Log
from packageship.application.models.package import PackagesMaintainer
from packageship.libs.dbutils import DBHelper
from packageship.libs.conf import configuration
from packageship.libs.exception import Error
from packageship.application.apps.lifecycle.function.concurrent import ProducerConsumer

LOGGER = Log(__name__)


# pylint: disable= too-few-public-methods
class SigInfo():
    """
    Description: read sig info from yaml file, parse sig info,
    if the package name is already in the database,
    update the sig info, otherwise insert the sig info

    Attributes:
        headers
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW 64; rv:50.0) Gecko/20100101 \
                Firefox / 50.0 '}

    @retry(stop_max_attempt_number=3, stop_max_delay=1000)
    def __read_sigs_content(self):
        """
        Description: read sig data from yaml file
        Args:
        Returns:
            sigs_dict
        Raises:
            FileNotFoundError: yaml file not found
            YAMLError: yaml format error
            HTTPError: http request error
        """
        try:
            sig_url = configuration.SIG_URL
            if not sig_url:
                _msg = "sig url configuration path does not exist or cannot be found"
                raise Error(_msg)

            response = requests.get(sig_url, headers=self.headers)
            if response.status_code != 200:
                _msg = "There is an exception with the remote service [%s]，" \
                       "Please try again later.The HTTP error code is：%s" % (sig_url, str(
                    response.status_code))
                raise HTTPError(_msg)

            sigs_content = yaml.load(response.content, Loader=yaml.FullLoader)
            if sigs_content is None or not isinstance(sigs_content, dict):
                _msg = ("the sigs content is empty, or the sigs "
                        "content is not in dict format")
                LOGGER.logger.error(_msg)
                return None

            sigs_dict = {}
            for sig in sigs_content['sigs']:
                for element in sig['repositories']:
                    sigs_dict[element] = sig['name']
            return sigs_dict
        except (yaml.YAMLError, FileNotFoundError, HTTPError, RequestException) as error:
            LOGGER.logger.error(
                'An abnormal error occurred while reading sig content from yaml file:%s '
                % error if error else '')
            return None

    def __parse_sigs_data(self):
        """
        Description: parse sigs data
        Args:
        Returns:
            parsed_sigs_dict: the parsed sig dict according yaml file
        """
        parsed_sigs_dict = dict()
        sigs_data = self.__read_sigs_content()
        if not sigs_data or not isinstance(sigs_data, dict):
            _msg = ("the sigs content is empty, or the sigs "
                    "content is not in dict format")
            LOGGER.logger.error(_msg)
            return None

        for key, value in sigs_data.items():
            if key.startswith('src-openeuler/'):
                pkg_name = key.split('/')[1]
                parsed_sigs_dict[pkg_name] = value
            else:
                if key.split('/')[1] not in parsed_sigs_dict.keys():
                    pkg_name = key.split('/')[1]
                    parsed_sigs_dict[pkg_name] = value
        return parsed_sigs_dict

    @staticmethod
    def __update_sig_data(insert_dict):
        """
        Description: If the package name is already in the database,
        update the sig info, otherwise insert the sig info
        Args:
        Returns:
        Raises:
            SQLAlchemyError: sqlalchemy error
        """
        try:
            with DBHelper(db_name="lifecycle") as data_base:
                packages_maintainer_objs = data_base.session.query(  # pylint: disable= no-member
                    PackagesMaintainer).all()

                for obj in packages_maintainer_objs:
                    if obj.name in insert_dict:
                        if obj.sig != insert_dict[obj.name]:
                            obj.sig = insert_dict[obj.name]
                        del insert_dict[obj.name]
                data_base.session.commit()  # pylint: disable= no-member
                insert_list = [
                    {'name': new_name, 'sig': new_sig}
                    for new_name, new_sig in insert_dict.items()
                ]

                if insert_list:
                    data_base.batch_add(insert_list, PackagesMaintainer)

        except SQLAlchemyError as error_msg:
            LOGGER.logger.error('update or add sig data faild: %s '
                                % error_msg if error_msg else '')
        else:
            _msg = "Successfully save or update sig info."
            LOGGER.logger.info(_msg)

    def save_all_packages_sigs_data(self):
        """
        Description: save all packages sig info in packages_maintainer table
        Args:
        Returns: None. Save or update data successfully,it is visible in the log information
        Raises:
            SQLAlchemyError: sqlalchemy error. Failed to save data, the exception is recorded in
             the log
        """
        producer_consumer = ProducerConsumer()
        parsed_sigs_data = self.__parse_sigs_data()
        if not parsed_sigs_data:
            _msg = "empty parsed sig data."
            LOGGER.logger.error(_msg)
            return None

        db_file_path = os.path.join(configuration.DATABASE_FOLDER_PATH, "lifecycle.db")
        if not os.path.exists(db_file_path):
            LOGGER.logger.error("db file not exists")
            return None

        try:
            with DBHelper(db_name="lifecycle") as database:
                if 'packages_maintainer' not in database.engine.table_names():
                    _msg = "packages_maintainer table not exists."
                    LOGGER.logger.error(_msg)
                    return None

                name_in = literal_column('name').in_(parsed_sigs_data)
                pkg_names = set()
                for table_name in filter(
                        lambda x: x not in ['packages_issue',
                                            'packages_maintainer', 'databases_info'],
                        database.engine.table_names()):
                    sql_str = """
                                   SELECT NAME FROM {} where {}
                               """.format('`' + table_name + '`', name_in)

                    tmp_res = database.session.execute(  # pylint: disable= no-member
                        sql_str,
                        {'name_{}'.format(i): v
                         for i, v in enumerate(parsed_sigs_data.keys(), 1)}
                    ).fetchall()
                    pkg_names.update(set(obj.name for obj in tmp_res))

            to_insert_dict = {
                name: parsed_sigs_data[name] for name in pkg_names
            }

            producer_consumer.put((to_insert_dict, self.__update_sig_data))
            return None

        except SQLAlchemyError as error_msg:
            LOGGER.logger.error('update or add sig data faild: %s '
                                % error_msg if error_msg else '')
            return None
