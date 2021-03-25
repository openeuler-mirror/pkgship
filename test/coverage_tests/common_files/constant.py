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
class ResponseCode():
    """
    Description: response code to web
    changeLog:
    """
    # Four digits are common status codes
    SUCCESS = "200"
    PARAM_ERROR = "4001"
    DB_NAME_ERROR = "4002"
    PACK_NAME_NOT_FOUND = "4003"
    CONNECT_DB_ERROR = "4004"
    INPUT_NONE = "4005"
    FILE_NOT_FOUND = "4006"
    SPECIFIED_FILE_NOT_EXIST = "4007"
    UPDATA_OR_ADD_DATA_FAILED = "4008"
    TABLE_NAME_NOT_EXIST = "4009"
    UPDATA_DATA_FAILED = "4010"
    NOT_FOUND_DATABASE_INFO = "4011"
    # Database operation module error status code
    DELETE_DB_ERROR = "40051"
    SERVICE_ERROR = "50000"
    CONFIGFILE_PATH_EMPTY = "50001"
    FAILED_CREATE_DATABASE_TABLE = "50002"
    TYPE_ERROR = "50003"
    DATA_MERGE_ERROR = "50004"
    FILE_NOT_FIND_ERROR = "50005"
    DIS_CONNECTION_DB = "50006"
    FILELIST_TYPE_ERROR = "50007"
    NO_PACKAGES_TABLE = "60001"
    DATABASE_NOT_FOUND = "60002"
    TABLE_NAME_NOT_EXIST_IN_DATABASE = "60003"
    YAML_FILE_ERROR = " 70001"
    EMPTY_FOLDER = "70002"
    EMPTY_PARSED_DATA = "70003"

    CODE_MSG_MAP = {
        SUCCESS: "Successful Operation!",
        PARAM_ERROR: "Request parameter error",
        DB_NAME_ERROR: "Database does not exist",
        PACK_NAME_NOT_FOUND: "The querying package does not exist in the databases",
        CONNECT_DB_ERROR: "Failed to Connect the database",
        INPUT_NONE: "The input is None",
        FILE_NOT_FOUND: "File does not exist",
        DELETE_DB_ERROR: "Failed to delete database",
        CONFIGFILE_PATH_EMPTY: "Initialization profile does not exist or cannot be found",
        FAILED_CREATE_DATABASE_TABLE: "Failed to create database or table",
        TYPE_ERROR: "The source code and binary path types in the initialization file are abnormal",
        DATA_MERGE_ERROR: "Multi-file database integration error",
        FILE_NOT_FIND_ERROR: "System initialization configuration file does not exist",
        DIS_CONNECTION_DB: "Unable to connect to the database",
        FILELIST_TYPE_ERROR: "The package filetype is not in ['d', 'f', 'g']",
        SERVICE_ERROR: "An exception occurred in the system",
        SPECIFIED_FILE_NOT_EXIST: "The specified file does not exist",
        NO_PACKAGES_TABLE: "There is no packages table in the database",
        UPDATA_OR_ADD_DATA_FAILED: "Failed to update or add data",
        DATABASE_NOT_FOUND: "There is no such database in the system",
        TABLE_NAME_NOT_EXIST: "Table name dose not match the existed database",
        TABLE_NAME_NOT_EXIST_IN_DATABASE: "The table name dose not match the existed database",
        NOT_FOUND_DATABASE_INFO: "Unable to get the generated database information",
        YAML_FILE_ERROR: "Data error in yaml file",
        EMPTY_FOLDER: "This is an empty folder",
        EMPTY_PARSED_DATA: "The parsed yaml data is empty"
    }

    @classmethod
    def response_json(cls, code, data=None, msg=None):
        """
        Description: classmethod
        """
        try:
            _msg = cls.CODE_MSG_MAP[code]
        except KeyError:
            _msg = msg
        return {
            "code": code,
            "message": _msg,
            "resp": data
        }

    def __str__(self):
        return 'ResponseCode'


