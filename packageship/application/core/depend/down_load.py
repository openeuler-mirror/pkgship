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
File download logic processing
"""
import copy
import csv
import os
import uuid
from functools import wraps
from typing import Set
from packageship.application.core.pkginfo.pkg import Package
from packageship.libs.conf import configuration
from packageship.libs.log import LOGGER


def catch_error(func):
    """
    Exception capture decorator
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (
                KeyError, TypeError, ValueError, AttributeError, IndexError, TypeError) as error:
            LOGGER.error(error)
            raise ValueError("input json_data is error! please check")
        except (IOError, OSError) as error:
            LOGGER.error(error)
            raise ValueError("input json_data is error! please check")

    return inner


class Download:
    """
    Generate CSV files with four dependencies

    Attributes:
        depend_type: Type of dependency
        package_name: The name of the package
        full_depend_data: It all depends on the data
        package_type: The type of package
        install_data: All data of install
        build_data: All data of build
        binary_packages: binary packages list
        folder_path: folder path
        install_csv_writer: install_csv_writer
        build_csv_writer: build_csv_writer
        src_package_write：src_package_write
        bin_package_write：bin_package_write
    """
    pkg = Package()
    install_count = 4
    build_count = 3

    def __init__(self, depend=None):
        """
        Initialize class properties
        """
        if depend:
            self._depend = depend
            self.full_depend_data = self._depend.bedepend_dict
            self.install_data, self.build_data = self._depend.depend_dict
            self.depend_type = self._depend.dependency_type
            self.package_name = self._depend.packagename
        self.binary_packages = []
        self.folder_path = None
        self.install_csv_writer = None
        self.build_csv_writer = None
        self.src_package_write = None
        self.bin_package_write = None
        self.database_name = None

    def __create_folder_path(self):
        """
        Method to create a folder
        Raises:
            IOError: Failed to create folder
        """
        self.folder_path = os.path.join(
            configuration.TEMPORARY_DIRECTORY, str(uuid.uuid1().hex))
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def _update_build_dict_data(self):
        """
        Change data in build data;Change the binary package to source package
        """
        if self.depend_type not in ["selfdep", "builddep"]:
            return

        if self.depend_type == "selfdep":
            for bin_pkg, vals in self.install_data.items():
                if vals["source_name"] in self.package_name:
                    self.binary_packages.append(bin_pkg)
        new_build_data = dict()
        for src_package, src_dict in self.build_data.items():
            new_build_data[src_package] = {
                "version": src_dict["version"],
                "database": src_dict["database"],
                "build": []
            }
            for bin_package in src_dict.get('build', []):
                bin_package_name = self.install_data.get(bin_package)
                if bin_package_name:
                    source_package_name = bin_package_name.get("source_name")
                    if source_package_name not in new_build_data[src_package]["build"]:
                        new_build_data[src_package]["build"].append(
                            source_package_name)

            if self.depend_type == "builddep":
                if src_package in self.package_name:
                    self.binary_packages.extend(src_dict["build"])
        self.build_data = new_build_data
        return

    def __process_full_depend_data_to_csv(self):
        """
        Write the full amount of data to CSVs
        """

        full_path = os.path.join(
            self.folder_path,
            "full_amount_data.csv")
        with open(full_path, "a+", newline="", encoding="utf-8") as full_depend_csv:
            full_depend_csv_writer = csv.writer(full_depend_csv)
            for key, values in self.full_depend_data.items():
                full_row_list = [
                    key,
                    values.get("source_name"),
                    values.get("version"),
                    values.get("database"),
                    *["install__" + str(bin) for bin in values.get("install", [])],
                    *["build__" + str(src) for src in values.get("build", [])]
                ]
                full_depend_csv_writer.writerow(full_row_list)

    def __get_single_df_row(self, pkg_name, res_type):
        """
        Get a row of data
        Args:
            pkg_name: package name
            res_type: The type of package

        Returns:
           list : A list of package information
        """
        if res_type == "install":
            if not self.install_data.get(pkg_name):
                return []
            else:
                return [
                    self.install_data.get(pkg_name)["source_name"],
                    self.install_data.get(pkg_name)["version"],
                    self.install_data.get(pkg_name)["database"]
                ]
        else:
            if not self.build_data.get(pkg_name):
                return []
            else:
                return [
                    self.build_data.get(pkg_name)["version"],
                    self.build_data.get(pkg_name)["database"],
                ]

    def __get_depends(self, pkg_name, get_type):
        """
        get depend
        Args:
            pkg_name: package name
            res_type: The type of package

        Returns:this data[n]'s deepcopy

        """
        if get_type == 'build':
            data = self.build_data
        else:
            data = self.install_data
        if pkg_name not in data:
            return []
        return copy.deepcopy(data[pkg_name].get(get_type, []))

    def __write_csv_update_df_row(
            self,
            lst,
            res_type,
            names_set: Set,
            pkg=None):
        """
        to write csv row and return new csv row list
        Args:
            lst:old csv row list
            res_type:install or build
            names_set:Store a list of package names that have been found
            pkg:package name

        Returns:
            new csv row list
        """
        local_lst = copy.deepcopy(lst)
        csv_writer = self.install_csv_writer if res_type == "install" else self.build_csv_writer
        if not pkg:
            csv_writer.writerow(local_lst)
            return lst

        names_set.add(pkg)
        new_row = self.__get_single_df_row(pkg, res_type)
        if not new_row:
            csv_writer.writerow(local_lst)
            return lst
        local_lst.extend([pkg, *new_row])
        if pkg in lst:
            # When a dependency chain is closed, add 1 to the end of a line in the CSV file
            local_lst.append("1")

        csv_writer.writerow(local_lst)

        return lst

    def __data_to_csv(self, pkg_name, names_set, res_type="install"):
        """
        process json data to save csv
        Args:
            pkg_name:search package name
            res_type:install or build

        Returns:

        """
        # When generating csv, need to pop up some contents of the data stack.
        # The pop-up number of install is 4. The number of pop-ups of  build is

        num = self.install_count if res_type == "install" else self.build_count
        _stack = [self.__get_depends(pkg_name, res_type)]
        rows = self.__get_single_df_row(pkg_name, res_type)
        if not rows:
            return names_set
        df_row = [pkg_name, *rows]
        while _stack:
            while not _stack[-1]:
                if len(_stack) == 1:
                    _stack.pop()
                    break
                _stack.pop()
                df_row = df_row[:-num]
            if not _stack:
                break

            next_pkg = _stack[-1].pop()

            if not next_pkg:
                continue

            if next_pkg not in df_row and next_pkg not in names_set:
                names_set.add(next_pkg)
                rows = self.__get_single_df_row(next_pkg, res_type)
                if not rows:
                    continue
                df_row.extend([next_pkg, *rows])

                depends = self.__get_depends(next_pkg, res_type)
                if depends:
                    _stack.append(depends)
                else:
                    df_row = self.__write_csv_update_df_row(
                        df_row, res_type, names_set)
                    df_row = df_row[:-num]
                    continue
            else:
                df_row = self.__write_csv_update_df_row(df_row,
                                                        res_type,
                                                        names_set,
                                                        pkg=next_pkg)

                continue
        return names_set

    def __write_install_csv(self):
        """
        Writes the data of the installed fetch to CSV
        Returns:

        """
        install_path = os.path.join(
            self.folder_path,
            "install_data.csv")
        with open(install_path, "a+", encoding="utf-8", newline="") as install_csv:
            self.install_csv_writer = csv.writer(install_csv)
            name_set = set()
            if self.binary_packages:
                for name in self.binary_packages:
                    name_set = self.__data_to_csv(name, name_set)
            else:
                for package_name in self.package_name:
                    name_set = self.__data_to_csv(package_name, name_set)

    def __write_build_csv(self):
        """
        Writes the retrieved build data to CSV
        Returns:

        """

        build_path = os.path.join(
            self.folder_path, "build.csv")
        with open(build_path, "a+", encoding="utf-8", newline="") as build_csv:
            self.build_csv_writer = csv.writer(build_csv)
            n_set = set()
            for package_name in self.package_name:
                n_set = self.__data_to_csv(
                    package_name, n_set, res_type="build")

    @catch_error
    def run(self):
        """
        main of this Class to run process data logic
        Returns:
            self.folder_path: folder path
        """

        if not any([self.build_data, self.install_data, self.full_depend_data]):
            return
        self._update_build_dict_data()
        self.__create_folder_path()
        self.__process_full_depend_data_to_csv()
        if self.depend_type == "bedep":
            return self.folder_path
        self.__write_install_csv()
        if self.depend_type == "selfdep":
            self.__write_build_csv()
        return self.folder_path

    def _all_bin_packages(self, database_name):
        """
        Gets information about all binary packages in the database
        Returns:
            all_bin_info: all binary packages information
        """
        all_bin_info = self.pkg.all_bin_packages(
            database_name, command_line=True)
        return all_bin_info

    def _all_src_packages(self, database_name):
        """
        Gets information about all source  packages in the database
        Returns:
            all_bin_info: all source  packages information
        """
        res = self.pkg.all_src_packages(database_name, command_line=True)
        return res

    @catch_error
    def process_packages(self, name, database_name):
        """
        Writes all package information to CSV

        Args:
            database_name: Specify the name of the database

        Returns:
            self.folder_path: Path to the folder
        """
        all_packages_info = {}
        if hasattr(self, "_all_{}_packages".format(name)):
            all_packages_info = getattr(
                self, "_all_{}_packages".format(name))(database_name)
        if not all_packages_info:
            return []
        self.__create_folder_path()
        package_info_path = os.path.join(
            self.folder_path, f"{database_name}_info.csv")
        with open(package_info_path,
                  "a+", newline="", encoding="utf-8") as bin_csv:
            bin_csv_writer = csv.writer(bin_csv)
            bin_csv_writer.writerow(["pkg_name",
                                     "license", "version", "url", "database"])
            for values in all_packages_info.get("data"):
                src_csv_row = [
                    values.get("pkg_name"),
                    values.get("license"),
                    values.get("version"),
                    values.get("url"),
                    values.get("database"),
                ]
                bin_csv_writer.writerow(src_csv_row)
        return self.folder_path
