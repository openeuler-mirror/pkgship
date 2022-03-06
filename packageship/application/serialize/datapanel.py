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


class _PublicQueryBase(Schema):
    pkg_name = fields.String(required=False, default=None)
    sig_name = fields.String(required=False, default=None)


class ExportObsinfoSchema(_PublicQueryBase):
    gitee_branch = fields.String(required=True, default="openEuler:20.03:LTS:SP1")
    architecture = fields.String(
        required=True,
        validate=validate.OneOf(["standard_aarch64", "standard_x86_64"]),
        default="standard_aarch64",
    )
    build_state = fields.String(required=False)


class ObsInfoListSchema(ExportObsinfoSchema):

    page_index = fields.Integer(default=-1)
    page_size = fields.Integer(default=100)


class PrInfoListSchema(_PublicQueryBase):
    maintainer_id = fields.String(required=False, default=None)
