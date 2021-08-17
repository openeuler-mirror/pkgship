#!/bin/bash
ENABLE_INSTALL=0
ENABLE_UNINSTALL=0
ENABLE_SERVICE=0
ENABLE_FUNCTION=0
WITH_DOCKER=1

function check_file_and_dir(){
	if [ ! -f /root/*.repo ];then
		echo "repo file does not exist in docker!"
		exit 1
	fi

	if [ ! -f /root/need_check_list ];then
		echo "file need_check_list does not exist in docker!"
		exit 1
	fi

	if [ ! -d /root/all_binary ];then
		echo "directory all_binary does not exist in docker!"
		exit 1
	fi
}

function config_yum(){
	for file in $(ls /etc/yum.repos.d/)
	do
		mv /etc/yum.repos.d/${file} /etc/yum.repos.d/${file}.bak
	done

	if [[ "${WITH_DOCKER}" -eq 1 ]]; then
		cp /root/*repo /etc/yum.repos.d/
	elif [[ "${WITH_DOCKER}" -eq 0 ]]; then
		cp ${yum_repo} /etc/yum.repos.d/
	fi

	if [ $? -ne 0 ]; then
		echo "copying yum repo file failed!"
		for file in $(ls /etc/yum.repos.d/*.bak)
		do
			old_name=$(echo ${file} | sed 's/.bak//g')
			mv ${file} ${old_name}
		done
		exit 1
	fi

	yum makecache &>/dev/null
	if [ $? -ne 0 ]; then
		echo "yum makecache failed!"
		exit 1
	fi
}

function check_pkg(){
	cd ${pre_path}
	mkdir -p ${pre_path}/check_result/success_log
	mkdir -p ${pre_path}/check_result/failed_log
	echo "Checking pkg is doing, please wait..."
	# install before checking function, service or uninstall
	if [[ "${ENABLE_FUNCTION}" -eq 1 ]] || [[ "${ENABLE_SERVICE}" -eq 1 ]] || [[ "${ENABLE_UNINSTALL}" -eq 1 ]]; then
		ENABLE_INSTALL=1
	fi

	for pkg in $(cat ${pre_path}/${pkglist})
	do
		if [[ "${ENABLE_INSTALL}" -eq 1 ]]; then
			check_install ${pkg}
		fi
		if [[ "${ENABLE_FUNCTION}" -eq 1 ]]; then
			check_function ${pkg}
		fi
		if [[ "${ENABLE_SERVICE}" -eq 1 ]]; then
			check_service ${pkg}
		fi
		if [[ "${ENABLE_UNINSTALL}" -eq 1 ]]; then
			check_uninstall ${pkg}
		fi
	done
}


function check_install(){
	# check pkg install
	pkg=$1
	echo "${pkg} is installing..."
	# get binary pkgs list
	cd ${pre_path}/all_binary/${pkg}/
	rpmlist=$(cat rpmlist)
	yum install -y ${rpmlist} > install_res 2>&1
	# verify
	if [ $(cat install_res | grep "Complete!") == "Complete!" ] &>/dev/null;then
		echo "${pkg} is installed successfully !!!"
		echo "${pkg}" >> ${pre_path}/check_result/succeed_install_pkglist
		mkdir -p ${pre_path}/check_result/success_log/${pkg}
		mv install_res ${pre_path}/check_result/success_log/${pkg}/
	else
		echo "${pkg} is installed failed !!!"
		echo "${pkg}" >> ${pre_path}/check_result/failed_install_pkglist
		mkdir -p ${pre_path}/check_result/failed_log/${pkg}
		mv install_res ${pre_path}/check_result/failed_log/${pkg}/
	fi
}

function check_function(){
	# function verify
	pkg=$1
	if [ -f ${pre_path}/check_result/success_log/${pkg}/install_res ];then
		echo "verifying ${pkg} function..."
		cd ${pre_path}/all_binary/${pkg}/
		rpmlist=$(cat rpmlist)
		function_list=$(rpm -ql ${rpmlist} | grep -E '/usr/s?bin')
		for function in ${function_list}
		do
			timeout 5 ${function} --help &> /dev/null || timeout 5 ${function} -h &> /dev/null || timeout 5 ${function} help &> /dev/null
			if [ $? -eq 0 ];then
				echo "verifying ${function} succeed!"
			else
				echo "verifying ${function} failed!"
				echo "${pkg} [${function}]" >> failed_function_list
			fi
		done
		
		if [ -f "failed_function_list" ];then
			mkdir -p ${pre_path}/check_result/failed_log/${pkg}
			mv failed_function_list ${pre_path}/check_result/failed_log/${pkg}/
			echo "${pkg}" >> ${pre_path}/check_result/failed_function_pkglist
		else
			echo "${pkg}" >> ${pre_path}/check_result/succeed_function_pkglist
		fi
	fi
}

function check_service(){
	# service verify
	pkg=$1
	if [ -f ${pre_path}/check_result/success_log/${pkg}/install_res ];then
		echo "verifying ${pkg} service..."
		cd ${pre_path}/all_binary/$pkg/
		rpmlist=$(cat rpmlist)
		service_list=$(rpm -ql ${rpmlist} | grep -E "\.service$" | awk -F "/" '{print $NF}')
		echo ${service_list} > service_list
		service_id=0
		for service in ${service_list}
		do
			service_id=$(expr ${service_id} + 1)
			service_res=""
			service_flag=true
			for action in "start" "status" "stop"
			do
				timeout 10 systemctl ${action} ${service} >> service_res 2>&1
				if [ $? -ne 0 ];then
					echo "${pkg} [${service}]" >> failed_service_list
					service_flag=false
					break
				fi
			done
			
			if [ ${service_flag} = true ];then
				echo "verifying ${service} succeed!"
				mv service_res ${pre_path}/check_result/success_log/${pkg}/service${service_id}
			else
				echo "verifying ${service} failed!"
				mkdir -p ${pre_path}/check_result/failed_log/${pkg}
				mv service_res ${pre_path}/check_result/failed_log/${pkg}/service${service_id}
			fi
		done
			
		if [ ${service_id} -eq 0 ];then
			echo "No service provides!"
		fi

		if [ -f "failed_service_list" ];then
			mv failed_service_list ${pre_path}/check_result/failed_log/${pkg}/
			echo "${pkg}" >> ${pre_path}/check_result/failed_service_pkglist
		else
			echo "${pkg}" >> ${pre_path}/check_result/succeed_service_pkglist
		fi
	fi
}

function check_uninstall(){
	# uninstall
	pkg=$1
	if [ -f ${pre_path}/check_result/success_log/${pkg}/install_res ];then
		echo "${pkg} is uninstalling..."
		cd ${pre_path}/all_binary/${pkg}/
		rpmlist=$(cat rpmlist)
		yum remove ${rpmlist} -y > uninstall_res 2>&1
		if [ $(cat uninstall_res | grep "Complete!") == "Complete!" ] &>/dev/null;then
			echo "${pkg} is uninstalled successfully !!!"
			echo "${pkg}" >> ${pre_path}/check_result/succeed_uninstall_pkglist
			mv uninstall_res ${pre_path}/check_result/success_log/${pkg}/
		else
			echo "${pkg} is uninstalled failed !!!"
			echo "${pkg}" >> ${pre_path}/check_result/failed_uninstall_pkglist
			mkdir -p ${pre_path}/check_result/failed_log/${pkg}
			mv uninstall_res ${pre_path}/check_result/failed_log/${pkg}/
		fi
	fi
}

config_yum

pkglist=need_check_list
ENABLE_INSTALL=$1
ENABLE_FUNCTION=$2
ENABLE_SERVICE=$3
ENABLE_UNINSTALL=$4
WITH_DOCKER=$5

if [[ "${WITH_DOCKER}" -eq 1 ]]; then
	pre_path="/root"
	check_file_and_dir
elif [[ "${WITH_DOCKER}" -eq 0 ]]; then
	pre_path=$(pwd)
	source /root/check.config
fi

check_pkg
