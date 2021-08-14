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
Validate args of compare command
"""
import os
import shutil

from packageship.application.common.constant import SUPPORT_QUERY_TYPE
from packageship.application.query import database

# Maximum number of supported databases
MAX_SUPPORT_DB = 4


def validate_args(depend_type, dbs, output_path):
    """
    validate args of compare command
    :param depend_type:
    :param dbs: input databases
    :param output_path:
    :return:
    """
    if not all((depend_type, dbs, output_path)):
        raise ValueError('[ERROR] Parameter error, please check the parameter and query again.')
    # verify depend type
    if depend_type not in SUPPORT_QUERY_TYPE:
        raise ValueError(f'[ERROR] Dependent type ({depend_type}) is not supported, please enter again.')
    # verify dbs
    _validate_dbs(dbs)
    # verify output_path
    if not os.path.isdir(output_path) or not _is_writable(path=output_path):
        raise ValueError(f'[ERROR] Output path ({output_path}) not exist or does not support user pkgshipuser writing.')


def _validate_dbs(dbs):
    """
    Verify that the input database is supported
    :param dbs: input dbs
    :return: None
    """
    if len(dbs) > MAX_SUPPORT_DB:
        raise ValueError(f'[ERROR] Supports up to four databases.')

    if len(dbs) != len(set(dbs)):
        raise ValueError(f'[ERROR] Duplicate database entered.')

    support_dbs = database.get_db_priority()
    for db in dbs:
        if db not in support_dbs:
            raise ValueError(f'[ERROR] Database ({db}) is not supported, please enter again.')
    if len(dbs) == 1:
        print('[WARNING] There is only one input database, '
              'and only dependent information files will be generated without data comparison.')


def _is_writable(path):
    """
    Verify whether user pkgshipuser has write permission to the output path
    :param path: cvs save path
    :return: True False
    """
    tmp_path = os.path.join(path, 'tmp_compare')
    try:
        os.mkdir(tmp_path)
    except PermissionError:
        return False
    finally:
        if os.path.isdir(tmp_path):
            shutil.rmtree(tmp_path)
    return True
