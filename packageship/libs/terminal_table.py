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
Description: Simple encapsulation of pretty table
Class: TerminalTable
"""
import os
from prettytable import PrettyTable


class TerminalTable(PrettyTable):
    """
    Description: Rewrite several methods in prettytable
    Attributes:
        bottom:Bottom display
        _vertical_char:Draw characters with vertical edges
    """

    def __init__(self, field_names=None, **kwargs):
        super().__init__(field_names, **kwargs)
        self.bottom = kwargs.get('bottom') or False
        self._vertical_char = kwargs.get('vertical_char') or self._unicode("")

    def _reduce_widths(self, columns, lpad, rpad):
        """
        Description: Handling over-width columns
        Args:
            columns:columns
            lpad:The number of spaces to the left of the column data
            rpad:The number of spaces to the right of the column data
        Returns:

        """
        extra_width = sum(self._widths) - columns + (lpad + rpad) * len(self._widths)
        avg_width = columns / len(self._widths)
        gt_avg = filter(lambda x: x > avg_width, self._widths)
        denominator = sum(
            [(item - avg_width) / avg_width * 1.0 for item in gt_avg])
        zoom_width = list()
        for width in self._widths:
            if width > avg_width:
                width = round(width - ((width - avg_width) / avg_width * 1.0) /
                              denominator * extra_width)
            zoom_width.append(width)
        self._widths = zoom_width
        if sum(self._widths) > columns:
            _max_val = max(self._widths)
            self._widths[self._widths.index(_max_val)] = _max_val - (sum(self._widths) - columns)

    def _compute_widths(self, rows, options):
        """
        Description: Calculated width
        Args:
            rows:row of data, should be a list with as many elements as the table
            options:option
        Returns:

        """
        super()._compute_widths(rows, options)
        lpad, rpad = self._get_padding_widths(options)
        # Total number of columns
        try:
            window_width = os.get_terminal_size().columns
        except OSError as os_error:
            window_width = 100
        _columns = window_width - len(self._widths) - 1
        if _columns < sum(map(lambda x: x + lpad + rpad, self._widths)):
            coefficient = 1
            self._reduce_widths(_columns, lpad, rpad)
        else:
            coefficient = _columns / (sum(map(lambda x: x, self._widths)) * 1.0)
            self._widths = list(
                map(lambda x: round(x * coefficient - lpad - rpad), self._widths))
            if sum(map(lambda x: x + lpad + rpad, self._widths)) > _columns:
                _max_val = max(self._widths)
                self._widths[self._widths.index(_max_val)] =\
                    _max_val - (sum(map(lambda x: x + lpad + rpad, self._widths)) - _columns)
