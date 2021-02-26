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
Validators for all package and single package interfaces
"""
from marshmallow import fields
from marshmallow import validate
from marshmallow import Schema
from marshmallow import validates
from marshmallow import ValidationError
from packageship.application.query import database
from packageship.application.common import constant
db_list = database.get_db_priority()


class PackageSchema(Schema):
    """
    Validators for all packages (source, binary)
    """
    database_name = fields.String(required=True)
    page_num = fields.Integer(
        required=True, validate=lambda x: x >= 1, default=1)
    page_size = fields.Integer(
        required=True, validate=lambda x: constant.MAXIMUM_PAGE_SIZE >= x >= 1, default=20)
    query_pkg_name = fields.String(required=False)
    command_line = fields.Boolean(required=False)

    @validates("database_name")
    def validate_name(self, database_name):
        """
        validate database name
        Args:
            database_name : database name

        Raises:
            ValidationError: The exception that failed to validate
        """
        if database_name not in db_list:
            raise ValidationError("The name is not passed in the database")


class SingleSchema(Schema):
    """
    Single package (source, binary) validator
    """
    database_name = fields.String(
        required=True, validate=validate.Length(min=1))
    pkg_name = fields.String(required=True, validate=validate.Length(min=1))

    @validates("database_name")
    def validate_name(self, database_name):
        """
        validate database name
        Args:
            database_name : database name

        Raises:
            ValidationError: The exception that failed to validate
        """
        if database_name not in db_list:
            raise ValidationError("The name is not passed in the database")
