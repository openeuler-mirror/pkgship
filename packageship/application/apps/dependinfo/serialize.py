#!/usr/bin/python3
"""
Description: marshmallow serialize
"""
from marshmallow import Schema
from marshmallow import fields
from marshmallow import ValidationError
from marshmallow import validate


class InstallDependSchema(Schema):
    """
    Description: Check installdepend interface
    """
    binaryName = fields.Str(validate=validate.Length(min=1, max=500),
                            required=True)
    db_list = fields.List(fields.String(), required=False, allow_none=True)


class BuildDependSchema(Schema):
    """
    Description: Check builddepend interface
    """
    sourceName = fields.Str(validate=validate.Length(min=1, max=200),
                            required=True)
    db_list = fields.List(fields.String(), required=False, allow_none=True)


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
    packagename = fields.Str(validate=validate.Length(min=1, max=200),
                             required=True)
    withsubpack = fields.Str(validate=_validate_withsubpack,
                             required=False, allow_none=True)
    dbname = fields.Str(validate=validate.Length(min=1, max=50),
                        required=True)


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
