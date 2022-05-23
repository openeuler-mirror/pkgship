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

from packageship.application.common.constant import OBS_X_ARCHITECTURE
from packageship.application.common.constant import OBS_A_ARCHITECTURE

from packageship.application.common.constant import DEFAULT_GIT_BRANCH


class _PublicQueryBase(Schema):
    """
    Basic parameter validator
    """
    pkg_name = fields.String(required=False, default=None)
    sig_name = fields.String(required=False, default=None)


class ExportObsinfoSchema(_PublicQueryBase):
    """
    obs csv file export validator
    """
    gitee_branch = fields.String(required=True, default=DEFAULT_GIT_BRANCH)
    architecture = fields.String(
        required=True,
        validate=validate.OneOf([OBS_A_ARCHITECTURE, OBS_X_ARCHITECTURE]),
        default=OBS_A_ARCHITECTURE,
    )
    build_state = fields.String(required=False)


class ObsInfoListSchema(ExportObsinfoSchema):
    """
    obs info parameter validator
    """
    page_index = fields.Integer(default=-1, validate=lambda x: x >= -1)
    page_size = fields.Integer(default=100, validate=lambda x: x >= 1)
