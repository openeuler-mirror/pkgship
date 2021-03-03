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
Depends and downloads the interface's parameter validator
"""
from marshmallow import Schema
from marshmallow import fields
from marshmallow import validate
from marshmallow import pre_load
from marshmallow import validates
from marshmallow import ValidationError
from packageship.application.query import database


def get_db():
    """
    Gets the database information in the database,
    An exception is already caught on the function side.
    An empty list is returned when an exception occurs
    Returns:
        db_list: Gets the database information in the database
    """
    db_list = database.get_db_priority()
    return db_list


class BaseParameterSchema(Schema):
    """
    Basic parameter validator
    """
    level = fields.Integer(
        required=False, validate=lambda x: x > 0, missing=0)
    packtype = fields.String(required=False, validate=validate.OneOf(
        ["source", "binary", ""]), missing="")
    self_build = fields.Boolean(required=False, missing=False)
    with_subpack = fields.Boolean(required=False, missing=False)
    search_type = fields.String(required=False, validate=validate.OneOf(["install", "build", ""]),
                                missing="")


class OtherdependSchema(BaseParameterSchema):
    """
    Install dependencies, build dependencies, and selfdepen validators
    """
    db_priority = fields.List(fields.String(),
                              required=False, missing=get_db(), default=get_db())

    @validates("db_priority")
    def validate_name(self, db_priority):
        """
        The database is a database in the system
        Args:
            db_priority: The priority of the database

        Returns:
            None
        Raises:
            ValidationError: Validation fails
        """
        res = any(filter(lambda db_name: db_name not in get_db(), db_priority))
        if len(db_priority) < 1 or res:
            raise ValidationError(
                "db_priority length less than one or Database priority error")


class BedependSchema(BaseParameterSchema):
    """
    The validator of the dependent parameter
    """
    db_priority = fields.List(fields.String(),
                              required=True)

    @validates("db_priority")
    def validate_name(self, db_priority):
        """
        The database is a database in the system
        Args:
            db_priority: The priority of the database

        Returns:
            None
        Raises:
            ValidationError: Validation fails
        """
        res = any(filter(lambda db_name: db_name not in get_db(), db_priority))
        if len(db_priority) != 1 or res:
            raise ValidationError(
                "db_priority length less than one or Database priority error")


class DependSchema(Schema):
    """
    Install, build, selfbuild, bedepend validators
    """

    packagename = fields.List(
        fields.String(), required=True, validate=validate.Length(min=1))
    depend_type = fields.String(required=True, validate=validate.OneOf(
        ["installdep", "builddep", "selfdep", "bedep"]))
    node_name = fields.String(required=True)
    node_type = fields.String(
        required=True, validate=validate.OneOf(["binary", "source"]))
    parameter = fields.Nested(OtherdependSchema, required=False)

    @pre_load
    def _update_paramter(self, data, **kwargs):
        """
        update_paramter
        Args:
            data: parameter
        Returns:
            data: Parameters after processing
        """
        if data.get('depend_type') == "bedep":
            self.__dict__["load_fields"]["parameter"] = \
                fields.Nested(BedependSchema, required=True)

        return data


class DownSchema(Schema):
    """
    Download the parameter validator for the interface
    """

    packagename = fields.List(
        fields.String(), required=True, validate=validate.Length(min=1))
    depend_type = fields.String(required=True, validate=validate.OneOf(
        ["installdep", "builddep", "selfdep", "bedep", "src", "bin"]))
    parameter = fields.Nested(OtherdependSchema, required=False)

    @pre_load
    def _update_paramter(self, data, **kwargs):
        """
        update_paramter
        Args:
            data: parameter
        Returns:
            data: Parameters after processing
        """
        if data.get('depend_type') in ["bedep", "src", "bin"]:
            self.__dict__["load_fields"]["parameter"] = \
                fields.Nested(BedependSchema, required=True)

        return data
