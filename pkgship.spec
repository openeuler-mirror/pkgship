Name:           pkgship
Version:        2.1.0
Release:        2
Summary:        Pkgship implements rpm package dependence ,maintainer, patch query and so no.
License:        Mulan 2.0
URL:            https://gitee.com/openeuler/pkgship
Source0:        https://gitee.com/openeuler/pkgship-%{version}.tar.gz

BuildArch:      noarch

BuildRequires: shadow
BuildRequires: python3-flask-restful python3-flask python3 python3-pyyaml python3-redis
BuildRequires: python3-prettytable python3-requests python3-retrying python3-coverage
BuildRequires: python3-marshmallow python3-uWSGI python3-gevent python3-Flask-Limiter 
BuildRequires: python3-elasticsearch

Requires: python3-flask-restful python3-flask python3 python3-pyyaml python3-redis
Requires: python3-prettytable python3-requests python3-retrying python3-coverage
Requires: python3-marshmallow python3-uWSGI python3-gevent python3-Flask-Limiter 
Requires: python3-elasticsearch

%description
Pkgship implements rpm package dependence ,maintainer, patch query and so no.

%prep
%autosetup -n pkgship-%{version}

%build
%py3_build
current_path=`pwd`
cd $current_path'/packageship'
version_=%{version}
release_=%{release}
version_file=version.yaml
if [ -f "$version_file" ];then
        rm -rf $version_file
fi
touch $version_file
echo "create version.yaml successfully."
echo "Version: $version_" >> $version_file
echo "Release: $release_" >> $version_file

%install
%py3_install


%check
%{__python3} -m unittest test/coverage_count.py

%pre
user=pkgshipuser
group=pkgshipuser

#create group if not exists
egrep -w "^$group" /etc/group >& /dev/null
if [ $? -ne 0 ]
then
            groupadd $group
fi

#create user if not exists
egrep -w "^$user" /etc/passwd >& /dev/null
if [ $? -ne 0 ]
then
            useradd -g $group $user
fi


# create dir or file if not exists
function create_dir_file(){
if [ $3 = "d" ];then
        if [ ! -d "$1" ];then
                mkdir -p -m $2 $1
        fi
elif [ $3 = "f" ];then
        if [ -f $1 ];then
                        rm -rf $1
        fi
        touch $1
        chmod $2 $1
fi
chown -R $user:$group $1
}

create_dir_file /opt/pkgship_tmp 750 d
create_dir_file /var/log/pkgship 750 d
create_dir_file /var/log/pkgship-operation 600 d
create_dir_file /home/pkgusers/log 755 d
create_dir_file /home/pkgusers/uswgi 755 d
create_dir_file /etc/logrotate.d/pkgship 644 f

%post

%postun


%files
%doc README.md
%attr(0750,pkgshipuser,pkgshipuser) %{python3_sitelib}/*
%attr(0755,pkgshipuser,pkgshipuser) %config %{_sysconfdir}/pkgship/*
%attr(0755,pkgshipuser,pkgshipuser) %{_bindir}/pkgshipd
%attr(0755,pkgshipuser,pkgshipuser) %{_bindir}/pkgship
%attr(0750,root,root) /etc/pkgship/auto_install_pkgship_requires.sh
%attr(0640,pkgshipuser,pkgshipuser) /etc/pkgship/package.ini
%attr(0644,pkgshipuser,pkgshipuser) /etc/pkgship/conf.yaml
%attr(0640,pkgshipuser,pkgshipuser) /lib/systemd/system/pkgship.service

%changelog
* Fri Feb 27 2021 Yiru Wang  <wangyiru1@huawei.com>
- change pkgship's files owner and permisson
- change pkgship's database from sqlite to elasticsearch
- modify pkgship's BuildRequires and Requires

* Thu Jan 14 2021 Shenmei Tu  <tushenmei@huawei.com>
- Add unit test for all src packages interface

 Tue Jan 5 2021 Shenmei Tu <tushenmei@huawei.com>
- Analyze bedepend and selfbuild dependency result for command line

* Thu Dec 17 2020 Yiru Wang  <wangyiru1@huawei.com>
- Add the basic schema file for pkgship based on elasticsearch

* Wed Dec 23 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Four kinds of dependent zip download batch upload - Write the parsed data to CSV part of the code for uploading

* Tue Dec 22 2020 Shenmei Tu <tushenmei@huawei.com>
- Analyze install and build dependency result for command line

* Mon Dec 21 2020 Chengqiang Bao <baochengqiang1@huawei.com>
- SingleGraph interface should be modified in response to the modification of Level and Batch

* Mon Dec 21 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Four kinds of dependent zip download batch upload - be_depend data parsing

* Tue Dec 17 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Four kinds of dependent zip download batch upload - build dependent data parsing

* Thu Dec 17 2020 Chengqiang Bao <baochengqiang1@huawei.com>
- Add not_found_packages in output result for be depend interface

* Thu Dec 17 2020 Chengqiang Bao <baochengqiang1@huawei.com>
- Add level and batch query for dependinfo bedepend,installdepend,builddepend interface

* Thu Dec 17 2020 Chengqiang Bao <baochengqiang1@huawei.com>
- Add not_found_packages in output result for be depend interface

* Tue Dec 15 2020 Shenmei Tu <tushenmei@huawei.com>
- Add batch query for self depend interface and dependinfo self depend interface

* Mon Dec 14 2020 Chengqiang Bao <baochengqiang1@huawei.com>
- Add level and batch query for build depend interface

* Mon Dec 14 2020 Shenmei Tu <tushenmei@huawei.com>
- Add not_found_packages in output result for install depend interface

* Fri Dec 11 2020 Shaowei Cheng <chenshaowei3@huawei.com>
- Echo effect optimization,constants file extraction

* Tue Dec 8 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Four kinds of dependent zip download batch upload - dependent data parsing

* Fri Dec 4 2020 Shaowei Cheng <chenshaowei3@huawei.com>
- Echo effect optimization

* Thu Dec 03 2020 Chengqiang Bao <baochengqiang1@huawei.com>
- Add level and batch query for be depend interface

* Mon Nov 30 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Four kinds of dependent zip download batch upload - dependent data parsing

* Mon Nov 30 2020 Shenmei Tu <tushenmei@huawei.com>
- Add level and batch query for install depend interface

* Mon Nov 30 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Modify the address of the database after successful initialization

* Sat Nov 28 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Test case refactoring-upload in batches 5

* Sat Nov 28 2020 Shenmei Tu <tushenmei@huawei.com>
- Test case refactoring-upload in batches 4

* Fir Nov 27 2020 Shenmei Tu <tushenmei@huawei.com>
- Test case refactoring-upload in batches 3

* Thu Nov 26 2020 Chengqiang Bao <baochengqiang1@huawei.com>
- Test case refactoring-upload in batches 2

* Wed Nov 25 2020 Shenmei Tu <tushenmei@huawei.com>
- Test case refactoring-upload in batches 1

* Mon Nov 23 2020 Shenmei Tu <tushenmei@huawei.com>
- Modification of add_sig_info interface bug, adding test cases for this interface

* Mon Nov 18 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Upload zip file download in batches-basic code

* Tue Nov 10 2020 Shenmei Tu <tushenmei@huawei.com>
- New requirement: add filelist query interface

* Wed Nov 4 2020 Chengqiang Bao <baochengqiang1@huawei.com>
- pkgship add license to all files

* Wed Nov 4 2020 Shaowei Cheng <chenshaowei3@huawei.com>
- Solve the problem that the release time value cannot be obtained

* Tue Nov 3 2020 Shaowei Cheng <chenshaowei3@huawei.com>
- When the dependency graph in pkgship is aimed at the source code
  package display, the build type package will be used as its next dependency

* Tue Nov 3 2020 Yiru Wang <wangyiru1@huawei.com>
- Add the license file in the root directory of pkgship

* Tue Nov 3 2020 Xinxing Li <lixinxing6@huawei.com>
- Add loading status and modify issue-list interface

* Sat Oct 31 2020 Chengqiang Bao <baochengqiang1@huawei.com>
- The bedepend interface adds exception capture and modifies the accuracy
  of query results in special scenarios

* Sat Oct 31 2020 Chengqiang Bao <baochengqiang1@huawei.com>
- The web function adds an interface for obtaining installation dependent
  results, an interface for obtaining compile dependent results, and an
  interface for obtaining graphics.

* Thu Oct 29 2020 Shenmei Tu<tushenmei@huawei.com>
- New requirement: save "sig" information in the database

* Thu Oct 29 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Unit test refactoring, unit test of three interfaces

* Wed Oct 28 2020 Shaowei Cheng <chenshaowei3@huawei.com>
- Improve the /lifeCycle/issueTrace interface in pkgship

* Wed Oct 28 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Unit test reconstruction, basic framework submission

* Wed Oct 28 2020 Zhengtang Gong <gongzhengtang@huawei.com>
- pkgship initialization adds filelist data import, and replaces the
  previous local sqlite file import method with the form of repo source

* Thu Oct 22 2020 Pengju Jiang <jiangpengju2@huawei.com>
- Solve the problem of crash when calling get_all_package_info and sing_pack,
  and the problem of function return value error

* Wed Oct 21 2020 Zhengtang Gong <gongzhengtang@huawei.com>
- Modify the files involved in the configuration file

* Wed Oct 21 2020 Shaowei Cheng <chenshaowei3@huawei.com>
- Bug fix, add parameter checks of  pagenum, pagesize

* Tue Oct 13 2020 ZhangTao <zhangtao307@huawei.com> 1.1.0-14
- correct-the-parameter-transfer-method-and-change-the-status-recording-method.

* Fri Sep 25 2020 Cheng Shaowei <chenshaowei3@huawei.com> 1.1.0-13
- Optimize-log-records-when-obtaining-issue-content

* Fri Sep 25 2020 Zhang Tao <zhangtao307@huawei.com> - 1.1.0-12
- In the selfbuild scenario, add the error message that the software package cannot be found 

* Fri Sep 25 2020 Zhang Tao <zhangtao307@huawei.com> - 1.1.0-11
- Fix the problem of function parameters

* Thu Sep 24 2020 Yiru Wang <wangyiru1@huawei.com> - 1.1.0-10
- rm queue_maxsize param from package.ini and this parameter is not customizable

* Tue Sep 21 2020 Shenmei Tu <tushenmei@huawei.com> - 1.0-0-9
- Solve the problem of data duplication, increase the maximum queue length judgment, 
- and avoid occupying too much memory

* Mon Sep 21 2020 Shenmei Tu <tushenmei@huawei.com> - 1.0-0-8
- Add the judgment of whether the subpack_name attribute exists, fix the code indentation problem, 
- and reduce the judgment branch of the old code.

* Mon Sep 21 2020 Shenmei Tu <tushenmei@huawei.com> - 1.0-0-7
- fix the error when executing query commands

* Mon Sep 21 2020 Shenmei Tu <tushenmei@huawei.com> - 1.0-0-6
- When initializing logging, modify the incoming class object to an instance of the class,
- ensure the execution of internal functions,and read configuration file content

* Mon Sep 21 2020 Shenmei Tu <tushenmei@huawei.com> - 1.0-0-5
- Fix the problem of continuous spaces in message information in log records

* Thu Sep 17 2020 Shenmei Tu <tushenmei@huawei.com> - 1.0-0-4
- Modify the query logic of package information, reduce redundant queries and align dnf query results, 
- extract multiplexing functions, add corresponding docString, and clear pylint

* Fri Sep 11 2020 Yiru Wang <wangyiru1@huawei.com> - 1.1.0-3
- #I1UCM8, #I1UC8G: Modify some config files' permission issue;
- #I1TIYQ: Add concurrent-log-handler module to fix log resource conflict issue
- #I1TML0: Fix the matching relationship between source_rpm and src_name

* Tue Sep 1 2020 Zhengtang Gong <gongzhengtang@huawei.com> - 1.1.0-2
- Delete the packaged form of pyinstaller and change the execution
  of the command in the form of a single file as the input

* Sat Aug 29 2020 Yiru Wang <wangyiru1@huawei.com> - 1.1.0-1
- Add package management features:
  RPM packages statically displayed in the version repository
  RPM packages used time displayed for current version in the version repository
  Issue management of packages in a version-management repository

* Fri Aug 21 2020 Chengqiang Bao < baochengqiang1@huawei.com > - 1.0.0-7
- Fixed a problem with command line initialization of the Filepath parameter where relative paths are not supported and paths are too long

* Wed Aug 12 2020 Zhang Tao <zhangtao306@huawei.com> - 1.0.0-6
- Fix the test content to adapt to the new data structure, add BuildRequires for running %check

* Mon Aug 10 2020 Zhengtang Gong <gongzhengtang@huawei.com> - 1.0-5
- Command line supports calling remote services

* Wed Aug 5 2020 Yiru Wang <wangyiru1@huawei.com> - 1.0-4
- change Requires rpm pakcages' name to latest one

* Mon Jul 13 2020 Yiru Wang <wangyiru1@huawei.com> - 1.0-3
- run test cases while building

* Sat Jul 4 2020 Yiru Wang <wangyiru1@huawei.com> - 1.0-2
- cheange requires python3.7 to python3,add check pyinstaller file.

* Tue Jun 30 2020 Yiru Wang <wangyiru1@huawei.com> - 1.0-1
- add pkgshipd file

* Thu Jun 11 2020 Feng Hu <solar.hu@foxmail.com> - 1.0-0
- add macro to build cli bin when rpm install

* Sat Jun 6 2020 Feng Hu  <solar.hu@foxmail.com> - 1.0-0
- init package