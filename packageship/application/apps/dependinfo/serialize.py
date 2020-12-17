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
Description: marshmallow serialize
"""
from marshmallow import Schema
from marshmallow import fields
from marshmallow import ValidationError
from marshmallow import validate


def validate_level(level):
    """
    Description: the default value of level is -1, then query all the install depend.
    When user input level > 0, then query the corresponding level of install depend
    Args：
    Returns:
    Raises: ValidationError
    """
    if int(level) < -1 or int(level) == 0:
        raise ValidationError("level is illegal data ")


class InstallDependSchema(Schema):
    """
    Description: Check installdepend interface
    """
    binaryName = fields.List(fields.String(validate=validate.Length(
        min=1, max=200)), required=True, allow_none=False)
    db_list = fields.List(fields.String(), required=False, allow_none=True)
    level = fields.Integer(validate=validate_level, required=False, allow_none=True)


class BuildDependSchema(Schema):
    """
    Description: Check builddepend interface
    """
    sourceName = fields.List(fields.String(validate=validate.Length(
        min=1, max=200)), required=True, allow_none=False)
    db_list = fields.List(fields.String(), required=False, allow_none=True)
    level = fields.Integer(validate=validate_level, required=False, allow_none=True)


def _validate_withsubpack(withsubpack):
    """
    Description: Verify optional parameters withsubpack
    Args：
        withsubpack: withsubpack
    Returns:
        True or failure
    Raises:
        ValidationError:
    """
    if withsubpack not in ['0', '1']:
        raise ValidationError("withSubpack is illegal data ")


class BeDependSchema(Schema):
    """
    Description: Check bedepend interface
    """
    packagename = fields.List(fields.String(validate=validate.Length(
        min=1, max=200)), required=True, allow_none=False)
    withsubpack = fields.Str(validate=_validate_withsubpack,
                             required=False, allow_none=True)
    dbname = fields.Str(validate=validate.Length(min=1, max=50),
                        required=True)
    level = fields.Integer(validate=validate_level, required=False, allow_none=True)


def _validate_selfbuild(selfbuild):
    """
    Description: Verify optional parameters selfbuild
    Args：
        selfbuild: selfbuild
    Returns:
        True or failure
    Raises:
        ValidationError:
    """
    if selfbuild not in ['0', '1']:
        raise ValidationError("selfbuild is illegal data ")


def _validate_packtype(packagetype):
    """
    Description: Verify optional parameters packtype
    Args：
        packtype: packtype
    Returns:
        True or failure
    Raises:
        ValidationError:
    """
    if packagetype not in ['source', 'binary']:
        raise ValidationError("packtype is illegal data ")


class SelfDependSchema(Schema):
    """
    Description: Check selfdepend interface
    """
    packagename = fields.Str(validate=validate.Length(min=1, max=200),
                             required=True)
    db_list = fields.List(fields.String(),
                          required=False, allow_none=True)
    selfbuild = fields.Str(validate=_validate_selfbuild,
                           required=False, allow_none=True)
    withsubpack = fields.Str(validate=_validate_withsubpack,
                             required=False, allow_none=True)
    packtype = fields.Str(validate=_validate_packtype,
                          required=False, allow_none=True)


def _validate_query_type(query_type):
    """
    Description: Verify optional parameters query_type
    Args：
        query_type: query_type
    Returns:
        True or failure
    Raises:
        ValidationError:
    """
    if query_type not in ['installdep', 'builddep', 'selfbuild', 'bedepend']:
        raise ValidationError("query_type is illegal data ")


class SingleGraphSchema(Schema):
    """
    Description: Check SingleGraph interface
    """
    packagename = fields.Str(validate=validate.Length(min=1, max=200),
                             required=True)

    dbname = fields.List(fields.String(), required=True, allow_none=True)

    query_type = fields.Str(validate=_validate_query_type,
                            required=True, allow_none=True)

    selfbuild = fields.Str(validate=_validate_selfbuild,
                           required=False, allow_none=True)

    withsubpack = fields.Str(validate=_validate_withsubpack,
                             required=False, allow_none=True)

    packagetype = fields.Str(validate=_validate_packtype,
                             required=False, allow_none=True)

    node_name = fields.Str(validate=validate.Length(min=1, max=50),
                           required=True)


def have_err_db_name(db_list, db_priority):
    """
    Description: have error database name method
    Args:
        db_list: db_list db list of inputs
        db_priority: db_priority default list
    Returns:
        If any element in db_list  is no longer in db_priority, return false
    Raises:
    """
    return any(filter(lambda db_name: db_name not in db_priority, db_list))
