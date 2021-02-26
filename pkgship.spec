Name:           pkgship
Version:        1.1.0
Release:        1
Summary:        Pkgship implements rpm package dependence ,maintainer, patch query and so no.
License:        Mulan 2.0
URL:            https://gitee.com/openeuler/pkgship
Source0:        https://gitee.com/openeuler/pkgship-%{version}.tar.gz

BuildArch:      noarch

Requires: python3-flask-restful python3-flask python3 python3-pyyaml python3-redis
Requires: python3-prettytable python3-requests python3-concurrent-log-handler
Requires: python3-marshmallow python3-uWSGI

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

%post

%postun


%files
%doc README.md
%{python3_sitelib}/*
%attr(0755,root,root) %config %{_sysconfdir}/pkgship/*
%attr(0755,root,root) %{_bindir}/pkgshipd
%attr(0755,root,root) %{_bindir}/pkgship

%changelog
* Thu Dec 23 2020 Yiru Wang  <wangyiru1@huawei.com> 
- Add the basic schema file for pkgship
