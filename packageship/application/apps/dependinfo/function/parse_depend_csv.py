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
Process the restful interface response data as required and save it to the corresponding csv file
"""
import copy
import csv
import os
import uuid
from typing import List
from functools import wraps
from packageship.libs.conf import configuration
from flask import current_app

from packageship.libs.constants import ListNode


def catch_error(func):
    """
    Exception capture decorator
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, TypeError, AttributeError, IndexError) as error:
            current_app.logger.error(error)
            raise ValueError("input json_data is error! please check")
        except IOError as io_error:
            current_app.logger.error(io_error)
            raise ValueError("There is an error in writing the file."
                             "Please confirm whether you have permission.")

    return inner


class BaseDep:
    """
    Basic methods for parsing data
    """

    def __init__(self):
        """
        Instantiate the underlying data structure
        """
        self.data = dict()
        self.install_dict = dict()
        self.build_dict = dict()

    @catch_error
    def _init_install_data(self, bin_name: str, lst: List):
        """
        init install dict data
        Args:
            bin_name:binary package name
            lst:csv row data

        Returns:
            None, Update the install_DICt of the object properties
        """

        if bin_name not in self.install_dict:
            self.install_dict[bin_name] = {
                "source_name": lst[ListNode.SOURCE_NAME],
                "version": lst[ListNode.VERSION],
                "db_name": lst[ListNode.DBNAME],
                "install": []
            }

    @catch_error
    def _process_install_dict(self, bin_name, parent_name):
        """
        Parse the Install data type
        Args:
            bin_name: Binary package name
            parent_name: The name of the parent node package

        Returns:
            Update the install_DICt of the object properties
        """
        if parent_name not in self.install_dict:
            self.install_dict[parent_name] = {
                "source_name": self.data.get(parent_name)[ListNode.SOURCE_NAME],
                "version": self.data.get(parent_name)[ListNode.VERSION],
                "db_name": self.data.get(parent_name)[ListNode.DBNAME],
                "install": [bin_name]}

        else:
            if bin_name not in self.install_dict[parent_name]["install"]:
                self.install_dict[parent_name]["install"].append(bin_name)


class SelfDep(BaseDep):
    """
    Self-compile dependent data types
    """

    def __init__(self, json_data, pack_type):
        """
        Initializing attribute
        Args:
            json_data: Self-compiled dependent data
            pack_type:The type of package
        """
        super(SelfDep, self).__init__()
        self.json_data = json_data
        self.pack_type = pack_type
        self.sub_packs = []
        self.version_data = dict()
        self.build_dict = dict()

    @catch_error
    def __init_data(self):
        """
        Get the data after it is parsed
        Returns:
            Update the version_data of the object properties
        """
        self.data = self.json_data["binary_dicts"]
        self.version_data = self.json_data["source_dicts"]

    @catch_error
    def _process_build_dict(self, bin_name, parent_name):
        """
        Parsed data type
        Args:
            bin_name: The name of the binary package
            parent_name: Parse the build data and get the data

        Returns:
            None
        """
        if parent_name not in self.build_dict:
            self.build_dict[parent_name] = {
                "version": self.version_data.get(parent_name)[ListNode.VERSION],
                "db_name": self.version_data.get(parent_name)[ListNode.SOURCE_NAME],
                "build": [self.data.get(bin_name)[ListNode.SOURCE_NAME]]}
        else:
            if self.data.get(bin_name)[ListNode.SOURCE_NAME] \
                    not in self.build_dict[parent_name]["build"]:
                self.build_dict[parent_name]["build"].append(
                    self.data.get(bin_name)[ListNode.SOURCE_NAME])

    @catch_error
    def __update_build_dict(self):
        """
        update build dict
        Returns:
            None, Update the build_dict for the object property
        """
        for k, val in self.version_data.items():
            if k not in self.build_dict:
                self.build_dict[k] = {
                    "version": val[ListNode.VERSION],
                    "db_name": val[ListNode.SOURCE_NAME],
                    "build": []
                }

    def __process_parent_nodes(self, bin_name, parent_nodes):
        """
        process origin data to install_dict (sometimes add install_dict)
        Args:
            bin_name: Binary package name
            parent_nodes: The parent node

        Returns:
            None, Update the associated properties of the object
        """
        for parent_name, depend_type in parent_nodes:

            if parent_name == 'root':
                self.sub_packs.append(bin_name)
                continue
            if hasattr(self, '_process_{}_dict'.format(depend_type)):
                dict_handler = getattr(self, '_process_{}_dict'.format(depend_type))
                dict_handler(bin_name, parent_name)

    def __process_data(self):
        """
        Parse the incoming data
        Returns:
            None, A method is called
        """
        self.__init_data()
        for bin_name, list_values in self.data.items():
            parent_nodes = list_values[ListNode.TAIL]
            if list_values[ListNode.SOURCE_NAME] == "source":
                continue
            self._init_install_data(bin_name, list_values)
            self.__process_parent_nodes(bin_name, parent_nodes)

        self.__update_build_dict()

    def run(self):
        """
        Method Start port
        Returns:
            self.data: Binary_dicts data retrieved from JSON data
            self.install_dict: Get install Dict from the JSON data
            self.build_dict: Get install Dict from the JSON data
            self.sub_packs:  A list of related dependent packages
        """
        self.__process_data()
        return self.data, self.install_dict, self.build_dict, self.sub_packs

    def __repr__(self):
        """
        The type, value, and so on of the object describe the information
        Returns:
            The type, value, and so on of the object describe the information
        """
        return ' process self_build {} data '.format(self.pack_type)

    def __str__(self):
        """
        Quickly learn the contents of the object
        Returns:
            Quickly learn the contents of the object
        """
        return ' process self_build {} data '.format(self.pack_type)


class InstallDep(BaseDep):
    """
    Install dependencies
    """

    def __init__(self, json_data, *args):
        """
        Initializing attribute
        Args:
            json_data: json data
            *args: Multiple parameters
        """
        super(InstallDep, self).__init__()
        self.json_data = json_data
        self.args = args

    @catch_error
    def __init_data(self):
        """
        Get the data for install_DICt
        Returns:
            None,Object update property
        """
        self.data = self.json_data["install_dict"]

    def __process_parent_nodes(self, bin_name, parent_nodes):
        """
        Parse data format
        Args:
            bin_name: Binary package name
            parent_nodes: The parent node

        Returns:
            None,Object update property
        """
        for parent_name, depend_type in parent_nodes:

            if parent_name == 'root':
                continue

            if depend_type == 'install':
                self._process_install_dict(bin_name, parent_name)
            else:
                continue

    def __process_data(self):
        """
        Parse data format

        Returns:
            Object update property
        """
        self.__init_data()
        for bin_name, list_values in self.data.items():
            parent_nodes = list_values[ListNode.TAIL]
            if list_values[ListNode.SOURCE_NAME] == "source":
                continue
            self._init_install_data(bin_name, list_values)
            self.__process_parent_nodes(bin_name, parent_nodes)

    def run(self):
        """
        The entry to the call function
        Returns:
            self.data: data
            self.install_dict: install dict
            dict(): An empty dictionary
            list(): An empty list
        """
        self.__process_data()
        # return install data and empty data
        return self.data, self.install_dict, dict(), list()

    def __repr__(self):
        """
        The type, value, and so on of the object describe the information
        Returns:
            The type, value, and so on of the object describe the information
        """
        return ' process {} {} data '.format(self.__class__, self.args[0])

    def __str__(self):
        """
        Quickly learn the contents of the object
        Returns:
            Quickly learn the contents of the object
        """
        return ' process {} {} data '.format(self.__class__, self.args[0])


class BuildDep(BaseDep):
    """
    BuildDep
    """

    def __init__(self, json_data, *args):
        """
        Initializing attribute
        Args:
            json_data: json data
            *args: args
        """
        super(BuildDep, self).__init__()
        self.json_data = json_data
        self.args = args
        self.build_depends = []

    @catch_error
    def __init_data(self):
        """
        Get the data for build_dict
        Returns:
            None,Object update property
        """
        self.data = self.json_data["build_dict"]

    def __process_parent_nodes(self, bin_name, parent_nodes):
        """
        Parsed data type
        Args:
            bin_name: Binary package name
            parent_nodes: The parent node

        Returns:
            Object update property
        """
        for parent_name, depend_type in parent_nodes:

            if parent_name == 'root':
                continue

            if depend_type == 'install':
                self._process_install_dict(bin_name, parent_name)
            if depend_type == 'build':
                self.build_depends.append(bin_name)

    def __process_data(self):
        """
        Parsed data
        Returns:
            Object update property
        """
        self.__init_data()
        for bin_name, list_values in self.data.items():
            parent_nodes = list_values[ListNode.TAIL]
            if list_values[ListNode.SOURCE_NAME] == "source":
                continue
            self._init_install_data(bin_name, list_values)
            self.__process_parent_nodes(bin_name, parent_nodes)

    def run(self):
        """
        The main entrance to the method
        Returns:
            self.data: data
            self.install_dict: install dict
            dict(): An empty dictionary
            list(): An empty list
        """
        self.__process_data()
        # return all data and install data and empty data and the source
        # package's first layer depends
        return self.data, self.install_dict, dict(), self.build_depends

    def __repr__(self):
        """
        The type, value, and so on of the object describe the information
        Returns:
            The type, value, and so on of the object describe the information
        """
        return ' process {} {} data '.format(self.__class__, self.args[0])

    def __str__(self):
        """
        Quickly learn the contents of the object
        Returns:
            Quickly learn the contents of the object
        """
        return ' process {} {} data '.format(self.__class__, self.args[0])


class BeDep(BaseDep):
    """
    BeDep
    """

    def __init__(self, json_data, *args):
        """
        Initializes object properties
        Args:
            json_data: json data
            *args: args
        """
        super(BeDep, self).__init__()
        self.json_data = json_data
        self.args = args

    @catch_error
    def __init_data(self):
        """
        Get the BeDepend data+
        Returns:
            None,Object update property
        """
        self.data = self.json_data["bedepend"]

    def __process_parent_nodes(self, bin_name, parent_nodes):
        """
        Parsed parent data
        Args:
            bin_name: Binary package name
            parent_nodes: The parent node

        Returns:
            Object update property
        """
        for parent_name, depend_type in parent_nodes:

            if parent_name == 'root':
                continue

            if depend_type == 'install':
                self._process_install_dict(bin_name, parent_name)

    def __process_data(self):
        """
        process data
        Args:

        Returns:
            Object update property
        """
        self.__init_data()
        for bin_name, list_values in self.data.items():
            parent_nodes = list_values[ListNode.TAIL]
            if list_values[ListNode.SOURCE_NAME] == "source":
                continue
            self._init_install_data(bin_name, list_values)
            self.__process_parent_nodes(bin_name, parent_nodes)

    def run(self):
        """
        The main entry of the function
        Returns:
            self.data: data
            self.install_dict: install dict
            dict(): An empty dictionary
            list(): An empty list
        """
        self.__process_data()
        # return all data and empty install data and empty data
        return self.data, self.install_dict, dict(), list()

    def __repr__(self):
        """
        The type, value, and so on of the object describe the information
        Returns:

        """
        return ' process {} {} data '.format(self.__class__, self.args[0])

    def __str__(self):
        """
        Quickly learn the contents of the object
        Returns:

        """
        return ' process {} {} data '.format(self.__class__, self.args[0])


class DataToCsv:
    """
    Process the restful interface response data as required
    and save it to the corresponding csv file
    """
    DATA_FACTORY = {
        "self_build": SelfDep,
        "install": InstallDep,
        "build": BuildDep,
        "be_depend": BeDep
    }

    def __init__(self,
                 search_name,
                 json_data,
                 search_type: str,
                 pack_type: str = None):
        """

        Args:
            search_name:The name of the package being queried
            json_data:Query result of the current package name,
                      similar to the json data returned by the interface.
                        examples:
                            {
                                "code":...,
                                "data":{...},
                            }
            search_type:Dependency type of query，excepted in ['self_build','install','build']
            pack_type:You need to specify pack_type=binary or
                      source when the query dependency is self_build

        Raises:
            ValueError: The types that need to be queried are not within the supported scope

        """

        if search_type not in self.DATA_FACTORY:
            raise ValueError(
                "search_type is error,excepted in ['self_build','install','build','bedepend']")

        if search_type == "self_build" and not pack_type:
            raise ValueError(
                "if search_type is self_build,excepted parameter pack_type in ['binary','source']"
                " when you init this class")

        self.current_process_class = self.DATA_FACTORY[search_type]

        self.folder_path = os.path.join(
            configuration.temporary_directory, f"{search_name}_csv_folder" + str(uuid.uuid1().hex))
        self.json_data = json_data
        self.pack_type = pack_type
        self.search_name = search_name
        self.search_type = search_type
        self.data = dict()

        self.install_dict = dict()
        self.build_dict = dict()
        self.binary_packages = []
        try:
            if not os.path.exists(self.folder_path):
                os.makedirs(self.folder_path)
        except IOError as io_error:
            current_app.logger.error(io_error)
            raise IOError("Failed to create folder")

        self.install_csv_writer = None
        self.build_csv_writer = None

    def __get_processed_data(self):
        """
        get processed data
        Returns:
            None
        """
        process_ins = self.current_process_class(
            self.json_data, self.pack_type)

        (self.data,
         self.install_dict,
         self.build_dict,
         self.binary_packages) = process_ins.run()

    @catch_error
    def __process_full_depend_data_to_csv(self):
        """
        The dependent data is stored in a CSV file
        Returns:

        """
        full_depend_csv = open(os.path.join(self.folder_path,
                                            self.search_name + "_full_amount_"
                                            + self.search_type + ".csv"),
                               "w", newline="")
        full_depend_csv_writer = csv.writer(full_depend_csv)

        for k, values in self.data.items():
            csv_row = [k,
                       values[ListNode.SOURCE_NAME],
                       values[ListNode.VERSION],
                       values[ListNode.DBNAME]]
            for parent_name, parent_type in values[ListNode.TAIL]:
                if parent_name != "root" and parent_name is not None:
                    csv_row.append(parent_name + "__" + parent_type)
            full_depend_csv_writer.writerow(csv_row)
        full_depend_csv.close()

    @catch_error
    def __get_single_df_row(self, k: str, res_type: str):
        """
        get single df row
        Args:
            k: dict's key
            res_type: install or build

        Returns:
            list: This includes the package name, version number, and database name
        """
        if res_type == "install":
            return [
                self.install_dict.get(k)["source_name"],
                self.install_dict.get(k)["version"],
                self.install_dict.get(k)["db_name"]
            ]
        return [
            self.build_dict.get(k)["version"],
            self.build_dict.get(k)["db_name"],
        ]

    @catch_error
    def __get_depends(self, num, get_type):
        """
        get depend
        Args:
            num: dict's key
            get_type: install or build
        Returns:
            this data[n]'s deepcopy
        """
        if get_type == 'build':
            data = self.build_dict
        else:
            data = self.install_dict
        if num not in data:
            return None
        return copy.deepcopy(data[num][get_type])
