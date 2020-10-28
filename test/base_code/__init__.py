#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
Set the location of package.ini in the unit test
"""
import os
from packageship import BASE_PATH

os.environ["SETTINGS_FILE_PATH"] = os.path.join(os.path.dirname(BASE_PATH),
                                                'test',
                                                'common_files',
                                                'package.ini')
