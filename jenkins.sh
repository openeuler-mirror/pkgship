#!/bin/bash
REPO_CONFIG_FILE="/etc/yum.repos.d/openEuler_pkgship.repo"
pkgship_spec_path="pkgship/pkgship.spec"
os_version="21.03"

function clear_env(){
  rm -rf /home/jenkins/rpmbuild || echo "clear env"
}

function update_repo()
{
  if [ ! -f ${REPO_CONFIG_FILE} ]; then
     sudo touch ${REPO_CONFIG_FILE}
  fi
  sudo bash -c "cat>${REPO_CONFIG_FILE}"<<EOF
[pkgship_openEuler-$os_version]
name=pkgship_openEuler-$os_version
baseurl=http://119.3.219.20:82/openEuler:/$os_version/standard_\$basearch/
enabled=1
gpgcheck=0
EOF
}

function prepare_rpmbuild_dir()
{
  mkdir -p /home/jenkins/rpmbuild
  cd /home/jenkins/rpmbuild
  mkdir -p BUILD BUILDROOT RPM RPMS SOURCES SPECS SRPMS
  cd -
}

function install_require() 
{
  sudo yum install rpm-build -y --enablerepo=pkgship_openEuler-$os_version
  sudo yum install python3-Flask-Limiter python3-coverage python3-elasticsearch python3-elasticsearch python3-flask python3-flask-restful python3-gevent python3-marshmallow python3-prettytable python3-pyyaml python3-redis python3-requests python3-retrying python3-uWSGI python3-concurrent-log-handler python3-mock -y --enablerepo=pkgship_openEuler-$os_version
  if [ $? -ne 0 ]; then
    echo "install require rpm failed"
    exit 1
  fi
}

function build_install_rpm()
{
  if [ ! -f ${pkgship_spec_path} ]; then
    echo "pkgship.spec file not exists."
    exit 1
  fi
  version=""
  while read line
  do
  if [[ $line =~ "Version" ]]
      then
        version=`echo ${line: 9} | sed 's/ //g'`
        break
  fi
  done <${pkgship_spec_path}
  pkgship_name="pkgship-"$version
  mv pkgship $pkgship_name
  tar -zcvf  /home/jenkins/rpmbuild/SOURCES/$pkgship_name.tar.gz $pkgship_name &>/dev/null
  cp $pkgship_name/pkgship.spec /home/jenkins/rpmbuild/SPECS/
  # build pkgship rpm
  rpmbuild  -bb  /home/jenkins/rpmbuild/SPECS/pkgship.spec
  # install pkgship rpm
  sudo yum install -y /home/jenkins/rpmbuild/RPMS/noarch/pkgship* --enablerepo=pkgship_openEuler-21.03
}

export TZ=Asia/Shanghai

clear_env
echo "clear env              ... done"

update_repo
echo "update repo            ... done"

install_require
echo "install required rpms  ... done"

prepare_rpmbuild_dir
echo "prepare rpmbuild dir   ... done"

build_install_rpm
