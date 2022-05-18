#!/bin/bash
REPO_CONFIG_FILE="/etc/yum.repos.d/openEuler_pkgship.repo"
pkgship_spec_path="pkgship/pkgship.spec"

function clear_env() {
  rm -rf /home/jenkins/rpmbuild || echo "clear env"
}

function prepare_rpmbuild_dir() {
  mkdir -p /home/jenkins/rpmbuild
  cd /home/jenkins/rpmbuild
  mkdir -p BUILD BUILDROOT RPM RPMS SOURCES SPECS SRPMS
  cd -
}

function install_require() {
  sudo dnf install dnf-plugins-core -y
  sudo dnf config-manager --set-disable update
  sudo dnf install rpm-build 'dnf-command(builddep)' -y
  state_1=$?
  sudo dnf builddep pkgship/pkgship.spec -y
  state_2=$?
  if [ ${state_1} -eq 1 -o ${state_2} -eq 1 ]; then
    echo "install require rpm failed"
    exit 1
  fi
}

function add_tmp_requires() {
  echo "[INFO] add python requires"
  sudo dnf install python3-devel -y
  pip install aiohttp==3.8.1 lxml==4.6.3 apscheduler --trusted-host https://repo.huaweicloud.com -i https://repo.huaweicloud.com/repository/pypi/simple
}

function build_install_rpm(){
  if [ ! -f ${pkgship_spec_path} ]; then
    echo "pkgship.spec file not exists."
    exit 1
  fi
  version=""
  while read line; do
    if [[ $line =~ "Version" ]]; then
      version=$(echo ${line:9} | sed 's/ //g')
      break
    fi
  done <${pkgship_spec_path}
  pkgship_name="pkgship-"$version
  mv pkgship $pkgship_name
  tar -zcvf /home/jenkins/rpmbuild/SOURCES/$pkgship_name.tar.gz $pkgship_name &>/dev/null
  cp $pkgship_name/pkgship.spec /home/jenkins/rpmbuild/SPECS/
  # build pkgship rpm
  rpmbuild -bb /home/jenkins/rpmbuild/SPECS/pkgship.spec
  # install pkgship rpm

  sudo dnf install -y /home/jenkins/rpmbuild/RPMS/noarch/pkgship*
}

export TZ=Asia/Shanghai

clear_env
echo "clear env              ... done"

install_require
echo "install required rpms  ... done"

#add_tmp_requires

prepare_rpmbuild_dir
echo "prepare rpmbuild dir   ... done"

build_install_rpm
echo "build install rpm   ... done"