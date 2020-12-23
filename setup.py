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
Package management program installation configuration
file for software packaging
"""
from distutils.core import setup

_CONFIG_PATH = "/etc/pkgship/"

setup(
    name='packageship',
    version='1.0',
    py_modules=[
        'packageship.application.__init__',
        'packageship.application.appglobal',
        'packageship.application.settings',
        'packageship.application.apps.__init__',
        'packageship.application.apps.package.url',
        'packageship.application.apps.package.view',
        'packageship.application.apps.dependinfo.view',
        'packageship.application.apps.dependinfo.url',
        'packageship.application.cli.base',
        'packageship.application.cli.cmd',
        'packageship.application.cli.commands.bedepend',
        'packageship.application.cli.commands.builddep',
        'packageship.application.cli.commands.db',
        'packageship.application.cli.commands.initialize',
        'packageship.application.cli.commands.installdep',
        'packageship.application.cli.commands.srcpkg',
        'packageship.application.cli.commands.binpkg',
        'packageship.application.cli.commands.selfbuild',
        'packageship.application.common.constant',
        'packageship.application.common.exc',
        'packageship.application.common.export',
        'packageship.application.common.rar',
        'packageship.application.common.remote',
        'packageship.application.common.rsp.content',
        'packageship.application.common.rsp.xmlmap',
        'packageship.application.core.depend.be_depend',
        'packageship.application.core.depend.build_depend',
        'packageship.application.core.depend.depend',
        'packageship.application.core.depend.graph',
        'packageship.application.core.depend.install_depend',
        'packageship.application.core.depend.self_depend',
        'packageship.application.core.pkginfo.pkg',
        'packageship.application.core.db_info',
        'packageship.application.initialize.integration',
        'packageship.application.initialize.repo',
        'packageship.application.query.depend',
        'packageship.application.query.pkg',
        'packageship.application.serialize.dependinfo',
        'packageship.application.serialize.package',
        'packageship.application.serialize.validate',
        'packageship.application.database.cache',
        'packageship.application.database.search',
        'packageship.application.database.session',
        'packageship.application.database.engine.__init__',
        'packageship.application.database.engine.elastic.__init__',
        'packageship.libs.log',
        'packageship.libs.conf.global_config',
        'packageship.manage',
        'packageship.selfpkg'
    ],
    requires=['prettytable (==0.7.2)',
              'Flask_RESTful (==0.3.8)',
              'Flask_Script (==2.0.6)',
              'Flask (==1.1.2)',
              'marshmallow (==3.5.1)',
              'PyYAML (==5.3.1)',
              'concurrent_log_handler (==0.9.17)',
              'requests (==2.21.0)',
              'uwsgi (==2.0.18)'],
    license='Dependency package management',
    long_description=open('README.md', encoding='utf-8').read(),
    author='gongzt',
    data_files=[
        (_CONFIG_PATH, ['packageship/package.ini', 'conf.yaml']),
        ('/usr/bin', ['packageship/pkgshipd', 'packageship/pkgship'])]
)
