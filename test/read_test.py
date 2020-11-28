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
import os
import unittest
import datetime
from test.base_code.my_test_runner import MyTestRunner
from test.test_module.packages_tests.test_licence import TestLicence

RUNNER = MyTestRunner()


def read_data_tests():
    """Test cases with read operations on data"""
    from test.test_module.dependent_query_tests.test_install_depend import TestInstallDepend
    from test.test_module.dependent_query_tests.test_self_depend import TestSelfDepend
    from test.test_module.dependent_query_tests.test_be_depend import TestBeDepend
    from test.test_module.repodatas_test.test_get_repodatas import TestGetRepodatas
    from test.test_module.dependent_query_tests.test_build_depend import TestBuildDepend
    from test.test_module.packages_tests.test_packages import TestPackages
    from test.test_module.single_package_tests.test_get_singlepack import TestGetSinglePack
    from test.test_module.lifecycle.test_maintainer import TestGetMaintainers
    from test.test_module.lifecycle.test_downloadexcel import TestDownloadExcelFile
    from test.test_module.lifecycle.test_get_issues import TestGetIssue
    from test.test_module.dependinfo_tests.test_dependinfo_self_depend import TestDependInfoSelfDepend
    from test.test_module.dependinfo_tests.test_dependinfo_be_depend import TestDependInfoBeDepend
    from test.test_module.dependinfo_tests.test_dependinfo_install_depend import TestDependInfoInstallDepend
    from test.test_module.dependinfo_tests.test_dependinfo_build_depend import TestDependInfoBuildDepend

    suite = unittest.TestSuite()

    classes = [TestInstallDepend, TestSelfDepend, TestBeDepend,
               TestGetRepodatas, TestBuildDepend, TestPackages,
               TestGetSinglePack, TestGetMaintainers, TestDownloadExcelFile,
               TestGetIssue, TestDependInfoBeDepend, TestDependInfoSelfDepend,
               TestDependInfoBuildDepend, TestDependInfoInstallDepend, TestLicence]
    for cls in classes:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(cls))
    return RUNNER.run(suite)


start_time = datetime.datetime.now()
result_4_read = read_data_tests()
stop_time = datetime.datetime.now()

print('\nA Read Test total of %s test cases were run： \nsuccessful:%s\tfailed:%s\terror:%s\n' % (
    int(result_4_read.testsRun),
    int(result_4_read.success_case_count),
    int(result_4_read.failure_case_count),
    int(result_4_read.err_case_count)
))

print('Read Test Total Time: %s' % (stop_time - start_time))
os.system("redis-cli shutdown")