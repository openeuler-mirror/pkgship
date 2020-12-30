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

from marshmallow import ValidationError


def _load(*args, **kwargs):
    """

    """
    try:
        verifier, data = args
        result = verifier().load(data, partial=kwargs.get("partial", ()))
    except ValidationError as err:
        errors = err.messages

    val = result["databases"]
    return None, None


def validate(verifier, data, load=False, partial=()):
    """

    """
    if not isinstance(data, dict):
        raise TypeError(
            "The content to verify needs to be of a dictionary type")

    if load:
        result, errors = _load(verifier, data, partial=partial)
    else:
        errors = verifier().validate(data, partial=partial)
        result = data
    return result, errors
