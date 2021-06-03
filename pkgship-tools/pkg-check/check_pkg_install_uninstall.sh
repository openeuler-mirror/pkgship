#!/bin/bash
source /etc/pkgship-tools/check.config
init_path=`pwd`

# check input and config
function check_input_and_config(){
	clear
	proj=$1
	pkglist=$2
	echo "Checking input and config, please wait..."
	# check input
	if [ $# -ne 2 ];then
		echo "Usage: bash $0 projname pkglist_file_name"
		exit 1
	fi

	if [ ! -f $pkglist ];then
		echo "package list file $pkglist does not exist!"
		exit 1
	fi
	# check osc env
	yum info installed osc &>/dev/null
	if [ $? -ne 0 ];then
		echo "osc is not installed!"
		exit 1
	fi

	osc search $proj | grep "matches for '$proj' in projects" &>/dev/null
	if [ $? -ne 0 ];then
		echo "osc command excuted failed, please check:"
		echo "  1. osc config may be invalid"
		echo "  2. project $proj may not exist"
		exit 1
	fi
	# check obs REPO and ARCH
	osc ls -b $proj | grep "^$obs_repo/$obs_arch$" &>/dev/null
	if [ $? -eq 1 ];then
		echo "obs REPO or ARCH is not valid!"
		exit 1
	fi
	# check yum repo file
	if [ ! -f "${yum_repo}" ]; then
		echo "yum repo file doesn't exist!!"
		exit 1
	fi
	# check docker url
	echo "Downloading docker image, please wait..."
	wget $docker_url
	if [ $? -ne 0 ];then
		echo "downloading docker image source failed!"
		exit 1
	fi
}

# get binary rpm packages list
function get_binary(){
	proj=$1
	pkglist=$2

	rm -rf ${init_path}/check_result ${init_path}/all_binary
	mkdir ${init_path}/all_binary
	echo "Get binary packages lists is doing, please wait..."
	for pkg in `cat ${pkglist}`
	do	
		rpmlist=""
	        # get a list of compiled binary packages
		for rpm in `osc ls -b $proj $pkg $obs_repo $obs_arch | grep '\.rpm$' | grep -v '.src.rpm' | grep -v 'debuginfo' | grep -v 'debugsource'`
			do
				rpm=${rpm%\-*}
				rpmlist="$rpmlist $rpm"
			done
		if [[ -z $rpmlist ]];then
			echo "Get ${pkg} binary packages list failed on obs server !!!"
			echo "Get ${pkg} binary packages list failed on obs server !!!" >> get_binary_failed
		else
			echo $rpmlist > rpmlist
			mkdir -p ${init_path}/all_binary/$pkg
			mv rpmlist ${init_path}/all_binary/$pkg
			echo "Get ${pkg} binary packages list succeed !!!"
		fi
	done
	echo "Get all binary packages lists have done!"
	cd ${init_path}/all_binary && ls > ${init_path}/need_check_list
	if [ ! -s ${init_path}/need_check_list ];then
		echo "All pkg have no binaries on obs server, do not need check !!!"
		rm -rf ${init_path}/need_check_list ${init_path}/all_binary ${init_path}/binaries ${init_path}/get_binary_failed 
		exit 1
	fi
}

# create docker env
function create_env(){
	cd ${init_path}
	echo "Creating docker env, please wait..."
	docker_image_source=$(echo ${docker_url} | awk -F "/" '{print $NF}')
	docker_image_name=$(docker load < ${docker_image_source} | sed 's/Loaded image: //g')
	rm $docker_image_source -f
        # clean previous docker env
	docker stop test_install &>/dev/null
	docker rm test_install &>/dev/null
    	# creat docker and cp files into docker env 
	docker run -itd --net=host --name=test_install --privileged=true ${docker_image_name} /usr/sbin/init &>/dev/null
	if [ $? -ne 0 ];then
		echo "creating docker failed!"
		exit 1
	fi
	# copy files into docker, will check files exist or not in script check_pkg_install_uninstall_indocker.sh
	docker cp ${yum_repo} test_install:/root/
	docker cp ${init_path}/all_binary test_install:/root/
	docker cp ${init_path}/need_check_list test_install:/root/
	docker cp ${init_path}/check_pkg_install_uninstall_indocker.sh test_install:/root/
	docker exec -it test_install bash -c 'echo "export TMOUT=0" >> /etc/bashrc && source /etc/bashrc 2>/dev/null && exit'
	docker restart test_install &>/dev/null
	echo "Create docker env completed !!!"
}

# start check
function main(){
	docker exec -it test_install /bin/bash -c "cd /root/ && bash check_pkg_install_uninstall_indocker.sh need_check_list"
	# get result from docker, then clear temporary files and docker env
	docker cp test_install:/root/check_result ./
	rm -rf ${init_path}/need_check_list
	mv ${init_path}/get_binary_failed ${init_path}/check_result/ &>/dev/null
	mv ${init_path}/all_binary ${init_path}/check_result/
	docker stop test_install &>/dev/null
	docker rm test_install &>/dev/null
	echo "Clear docker env complete !!!"
	echo "Checking install and uninstall is complete, you can see log file in directory: ${init_path}/check_result, please backup check_result dir !!!"
}

echo "=============================================Begin============================================="
check_input_and_config $@
# $1 obs_proj_name $2 pkglist_file_name
get_binary $1 $2
create_env
main
echo "=============================================End==============================================="
