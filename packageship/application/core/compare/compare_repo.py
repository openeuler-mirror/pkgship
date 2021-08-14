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
from collections import defaultdict

import csv
import os
import stat

from packageship.libs.log import LOGGER


class CompareRepo(object):
    """
    Data comparison
    """

    def __init__(self, out_path, dbs):
        """
        init
        :param out_path: csv and excel file path
        :param dbs: Databases to be compared
        """
        self.out_path = out_path
        self.databases = dbs

    def dbs_compare(self, dbs_depend_info):
        """
        Compare the dependent information in different databases, write it into a csv file and convert it to excel。
        :param dbs_depend_info: the dependent information in different databases
        :return: True/False
        """
        LOGGER.info('Start to compare the dependent information in different databases')
        if not dbs_depend_info:
            print('[ERROR] No data in all databases')
            return False
        try:
            # The first database is recorded separately as the benchmark database
            base_database = dbs_depend_info[0]
            base_depend_dict = defaultdict(list)
            self._write_data_to_csv(base_database, base_depend_dict)
            # The latter database is used as a comparison database record
            compare_depend_list = list()
            for compare_database in dbs_depend_info[1:]:
                compare_depend_dict = defaultdict(list)
                self._write_data_to_csv(compare_database, compare_depend_dict)
                compare_depend_list.append(compare_depend_dict)

            # Compare the dependency difference between base database and other databases
            self._compare_data(base_depend_dict, compare_depend_list)
            # Set file permissions
            self._set_file_permissions()
            return True
        except (ValueError, AttributeError) as e:
            print('[ERROR] Failed to save the data by comparing the difference, please check the log location')
            LOGGER.error(f'Failed to save the data by comparing the difference, message is {str(e)}')
            return False

    def _write_data_to_csv(self, depend_info, depend_info_dict):
        """
        Write dependent data to csv file
        :param depend_info: {database：[{rpm_name:{rpm_depend_info}}]}
        :param depend_info_dict: Record the relationship between the package name and the package dependency to
               facilitate subsequent comparisons
        :return: None
        """
        field_names = [FIELD.DEPENDENCY, FIELD.DEPENDENCY_PACKAGE,
                       FIELD.DEPENDENCY_VERSION, FIELD.DEPENDING_PACKAGE,
                       FIELD.DEPENDING_VERSION]
        for database, depend_data in depend_info.items():
            LOGGER.info(f'Save data of {database} to csv')
            csv_file = os.path.join(self.out_path, f'{database}.csv')
            with open(csv_file, 'w', encoding='utf-8') as file:
                csv_writer = csv.DictWriter(file, fieldnames=field_names)
                csv_writer.writeheader()
                self._write_data(csv_writer, depend_data, depend_info_dict)

    @staticmethod
    def _write_data(csv_writer, depend_data, depend_info_dict):
        """
        Write the dependency information of a single database into a csv file and record it.
        :param csv_writer: instance of csv writer
        :param depend_data: dependency information
        :param depend_info_dict: Dictionary used to record brief information
        :return: None
        """
        for rpm in depend_data:
            for rpm_name, rpm_info in rpm.items():
                # If there is no dependency, record the (package_name ->'')
                if not rpm_info.get('requires'):
                    _empty_depend = '->'.join((rpm_name, ''))
                    csv_writer.writerow(
                        {FIELD.DEPENDENCY: _empty_depend})
                    depend_info_dict[rpm_name] = [_empty_depend]
                    continue
                # Traverse the dependency information, write it to the csv file, and record it in the depend info dict
                already_record_binary = list()
                for depend_info in rpm_info.get('requires'):
                    _depend_binary_rpm = depend_info.get('com_bin_name', '')
                    # Since multiple components may be provided by the same binary package,
                    # it is necessary to de-duplicate the statistics of binary packages here
                    if _depend_binary_rpm and _depend_binary_rpm in already_record_binary:
                        continue

                    already_record_binary.append(_depend_binary_rpm)
                    _depend_map = '->'.join((rpm_name, _depend_binary_rpm))
                    # The binary package and the source package have different fields
                    _source_name = rpm_info.get('source_name', '') \
                        if 'source_name' in rpm_info else rpm_info.get('src_name', '')
                    # Write to csv file
                    csv_writer.writerow({
                        FIELD.DEPENDENCY: _depend_map,
                        FIELD.DEPENDENCY_PACKAGE: _source_name,
                        FIELD.DEPENDENCY_VERSION: rpm_info.get('src_version', ''),
                        FIELD.DEPENDING_PACKAGE: depend_info.get('com_src_name', ''),
                        FIELD.DEPENDING_VERSION: depend_info.get('com_src_version', '')
                    })
                    depend_info_dict[rpm_name].append(_depend_map)

    def _compare_data(self, base_depend_dict, compare_depend_list):
        """
        Compare the dependency difference between the base database and other databases, and write it to a csv file
        :param base_depend_dict: base database dependency info
        :param compare_depend_list: other databases dependency info
        :return: None
        """
        if not compare_depend_list:
            LOGGER.warning('There is only one database input, no comparison operation')
            return
        csv_file = os.path.join(self.out_path, 'compare.csv')
        with open(csv_file, 'w', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(self.databases)
            for rpm, dependency in base_depend_dict.items():
                _all_dependency_list = [dependency]
                for other_database in compare_depend_list:
                    _all_dependency_list.append(other_database.get(rpm, []))

                _all_dependency_set = set([info for single_db_info in _all_dependency_list for info in single_db_info])
                self._write_single_field(_all_dependency_list, _all_dependency_set, csv_writer)

    @staticmethod
    def _write_single_field(all_dependency_list, all_dependency_set, writer):
        """
        Traverse the dependencies of each software package in different databases and write them to a csv file
        :param all_dependency_list: A list of dependencies of a software package in all databases
        :param all_dependency_set: Union of dependencies in all databases
        :param writer: csv writer
        :return: None
        """
        for dependency_info in all_dependency_set:
            _current_write_line = list()
            for db_dependency in all_dependency_list:
                if dependency_info in db_dependency:
                    _current_write_line.append(dependency_info)
                else:
                    _current_write_line.append(FIELD.EMPTY_FIELD)
            writer.writerow(_current_write_line)

    def _set_file_permissions(self):
        """
        Set csv file permissions:644
        :return: None
        """
        for file in os.listdir(self.out_path):
            if file.endswith('.csv'):
                file_path = os.path.join(self.out_path, file)
                os.chmod(file_path, 0o644)


class FIELD:
    """
    csv field_name
    """
    # rpm -> build/install depend rpm
    DEPENDENCY = 'dependency'
    # source rpm name of left rpm
    DEPENDENCY_PACKAGE = 'dependency package'
    # source rpm version of left rpm
    DEPENDENCY_VERSION = 'dependency version'
    # source rpm name of right rpm
    DEPENDING_PACKAGE = 'depending package'
    # source rpm version of right rpm
    DEPENDING_VERSION = 'depending version'
    # empty field
    EMPTY_FIELD = '#N/A'
