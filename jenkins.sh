#!/bin/bash

function clear_env(){
	rm -rf /home/jenkins/rpmbuild || echo "clear env"
}

function update_repo()
{
sudo bash -c "cat>/etc/yum.repos.d/openeuler.repo"<<EOF
[openEuler-21.03]
name=openEuler-21.03
baseurl=http://119.3.219.20:82/openEuler:/21.03/standard_aarch64/
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
	sudo yum install rpm-build -y
	sudo yum install python3-Flask-Limiter python3-coverage python3-elasticsearch python3-elasticsearch python3-flask python3-flask-restful python3-gevent python3-marshmallow python3-prettytable python3-pyyaml python3-redis python3-requests python3-retrying python3-uWSGI python3-concurrent-log-handler python3-mock -y
}

function build_install_rpm()
{
    version=""
    while read line
    do
        if [[ $line =~ "Version" ]]
            then
            	   version=`echo ${line: 9} | sed 's/ //g'`
                   break
        fi
    done <pkgship/pkgship.spec
	pkgship_name="pkgship-"$version
  mv pkgship $pkgship_name
	tar -zcvf  /home/jenkins/rpmbuild/SOURCES/$pkgship_name.tar.gz $pkgship_name &>/dev/null
	cp $pkgship_name/pkgship.spec /home/jenkins/rpmbuild/SPECS/

	rpmbuild  -bb  /home/jenkins/rpmbuild/SPECS/pkgship.spec
  sudo yum install -y /home/jenkins/rpmbuild/RPMS/noarch/pkgship*
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
