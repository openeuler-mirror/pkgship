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
from redis import Redis, ConnectionPool
from packageship.libs.conf import configuration

REDIS_CONN = Redis(connection_pool=ConnectionPool(
    host=configuration.REDIS_HOST,
    port=configuration.REDIS_PORT,
    max_connections=configuration.REDIS_MAX_CONNECTIONS,
    decode_responses=True))
# es page size max value
MAX_PAGE_SIZE = 10000

# default page num
DEFAULT_PAGE_NUM = 1

# maximum page number allowed
MAXIMUM_PAGE_SIZE = 200

# under line char
UNDERLINE = "-"

# binary database,used for query binary rpm
BINARY_DB_TYPE = "binary"

# source database,used for query source rpm
SOURCE_DB_TYPE = "source"

# database type
DATABASE_ENGINE_TYPE = "elastic"

# index of default databases
DB_INFO_INDEX = "databaseinfo"

# index suffix of bedepend require
BE_DEPEND_TYPE = "bedepend"

# index suffix of install require
INSTALL_DEPEND_TYPE = "install"

# index suffix of build require
BUILD_DEPEND_TYPE = "build"

# components from provides field
PROVIDES_NAME = "provides.name"

# components from files field
FILES_NAME = "files.name"

# Depends on the radius of the sphere of the graph
LEVEL_RADIUS = 30

# node size shown in the map
NODE_SIZE = 25

# uwsig path
UWSIG_PATH = "/opt/pkgship/uwsgi/pkgship.ini"


class ListNode():
    """
    Description: Dethe structure of dict:
    {package_name: [source_name,
                dbname,
                [[parent_node_1, depend_type],[parent_node_2, depend_type],...]],
                check_tag]
    }
    changeLog:
    """

    SOURCE_NAME = 0
    VERSION = 1
    DBNAME = 2
    PARENT_LIST = 3
    # FOR PARENT LIST:
    PARENT_NODE = 0
    DEPEND_TYPE = 1
    # FOR PARSE DATA
    BUILD_POP_COUNT = 3
    INSTALL_POP_COUNT = 4
    TAIL = -1
    FLAG_TRUE = True
    FLAG_FALSE = False


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
        PARAM_ERROR: "Parameter error, please check the parameter and query again.",
        DB_NAME_ERROR: "Database does not exist! Please check the database name",
        PACK_NAME_NOT_FOUND: "Sorry! The querying package does not exist in the databases",
        CONNECT_DB_ERROR: "Failed to Connect the database! "
                          "Please check the database connection",
        INPUT_NONE: "The input is None, please check the input value.",
        FILE_NOT_FOUND: "Database import success file does not exist",
        DELETE_DB_ERROR: "Failed to delete database",
        CONFIGFILE_PATH_EMPTY: "Initialization profile does not exist or cannot be found",
        FAILED_CREATE_DATABASE_TABLE: "Failed to create database or table",
        TYPE_ERROR: "The source code and binary path types in the initialization file are abnormal",
        DATA_MERGE_ERROR: "abnormal multi-file database integration",
        FILE_NOT_FIND_ERROR: "system initialization configuration file does not exist",
        DIS_CONNECTION_DB: "Unable to connect to the database, check the database configuration",
        FILELIST_TYPE_ERROR: "The package filetype is not in ['d', 'f', 'g'], "
                             "please try again later",
        SERVICE_ERROR: "An exception occurred in the system, please try again later",
        SPECIFIED_FILE_NOT_EXIST: "The specified file does not exist",
        NO_PACKAGES_TABLE: "There is no packages table in the database",
        UPDATA_OR_ADD_DATA_FAILED: "Failed to update or add data",
        DATABASE_NOT_FOUND: "There is no such database in the system",
        TABLE_NAME_NOT_EXIST: "There is no such table in the database",
        UPDATA_DATA_FAILED: "Failed to update data",
        TABLE_NAME_NOT_EXIST_IN_DATABASE: "the table name dose not match the existed database",
        NOT_FOUND_DATABASE_INFO: "Unable to get the generated database information",
        YAML_FILE_ERROR: "Data error in yaml file",
        EMPTY_FOLDER: "This is an empty folder, no yaml file",
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
            "msg": _msg,
            "data": data
        }

    def __str__(self):
        return 'ResponseCode'


ERROR_CON = {
    "200": {
        "CONTENT": "Successful Operation!"},
    "JSON_DECODE_ERROR": {
        "ERROR_CONTENT": "",
        "HINT": "The content is not a legal json format,please check "
                "the parameters is valid"},
    # Too many request
    429: {
        "ERROR_CONTENT": "",
        "HINT": "Too many requests in a short time, please request again later"
    },
    "Too_many_request": {
        "ERROR_CONTENT": "",
        "HINT": "Too many requests in a short time, please request again later"},
    # Server error
    500: {"ERROR_CONTENT": "Server error",
          "HINT": "Please check the service and try again"},
    "CONN_ERROR": {
        "ERROR_CONTENT": "",
        "HINT": "Please check the connection and try again"},
    # PARAM_ERROR
    "4001": {
        "ERROR_CONTENT": "",
        "HINT": "Please check the parameter is valid and query again"},
    # DB_NAME_ERROR
    "4002": {
        "ERROR_CONTENT": "",
        "HINT": "Use the correct database name"},
    # PACK_NAME_NOT_FOUND
    "4003": {
        "ERROR_CONTENT": "",
        "HINT": "Use the correct package name and try again"},
    # CONNECT_DB_ERROR
    "4004": {
        "ERROR_CONTENT": "",
        "HINT": "Check the connection"},
    # INPUT_NONE
    "4005": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the input value is valid"},
    # FILE_NOT_FOUND
    "4006": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the file exists"},
    # SPECIFIED_FILE_NOT_EXIST
    "4007": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the specified file exists"},
    # UPDATE_OR_ADD_DATA_FAILED
    "4008": {
        "ERROR_CONTENT": "",
        "HINT": "Please check the command/data and try again"},
    # TABLE_NAME_NOT_EXIST
    "4009": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the table is valid"},
    # UPDATE_DATA_FAILED
    "4010": {
        "ERROR_CONTENT": "",
        "HINT": "Please check and try again"},
    # NOT_FOUND_DATABASE_INFO
    "4011": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the generated database information is valid"},
    # DELETE_DB_ERROR
    "40051": {
        "ERROR_CONTENT": "",
        "HINT": "Please check and try again"},
    # SERVICE_ERROR
    "50000": {
        "ERROR_CONTENT": "",
        "HINT": "Please check and try again"},
    # CONFIGFILE_PATH_EMPTY
    "50001": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the initialization profile is valid"},
    # FAILED_CREATE_DATABASE_TABLE
    "50002": {
        "ERROR_CONTENT": "",
        "HINT": "Please check the initialization profile and try again"},
    # TYPE_ERROR
    "50003": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the source code and binary path types in "
                "the initialization file are valid"},
    # DATA_MERGE_ERROR
    "50004": {
        "ERROR_CONTENT": "",
        "HINT": "Please check and try again"},
    # FILE_NOT_FIND_ERROR
    "50005": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure system initialization configuration file exists"},
    # DIS_CONNECTION_DB
    "50006": {
        "ERROR_CONTENT": "",
        "HINT": "Please check the database configuration and try again"},
    # FILELIST_TYPE_ERROR
    "50007": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the package filetype is valid"},
    # NO_PACKAGES_TABLE
    "60001": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the packages table is valid"},
    # DATABASE_NOT_FOUND
    "60002": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the database is valid"},
    # TABLE_NAME_NOT_EXIST_IN_DATABASE
    "60003": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the table name is valid"},
    # YAML_FILE_ERROR
    "70001": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the yaml file is valid"},
    # EMPTY_FOLDER
    "70002": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the yaml file exists"},
    # EMPTY_PARSED_DATA
    "70003": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the yaml file is valid"},
    # DOWNLOAD_FAILED
    "70004": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the file is valid"},
    # PACKSHIP_VERSION_ERROR
    "70005": {
        "ERROR_CONTENT": "",
        "HINT": "Make sure the file is valid"}
}
