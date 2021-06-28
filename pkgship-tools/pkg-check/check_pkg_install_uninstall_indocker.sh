#!/bin/bash
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
	for file in `ls /etc/yum.repos.d/`
	do
		mv /etc/yum.repos.d/$file /etc/yum.repos.d/$file.bak
	done
	cp /root/*repo /etc/yum.repos.d/

	if [ $? -ne 0 ]; then
		echo "copying yum repo file failed!"
		for file in `ls /etc/yum.repos.d/*.bak`
		do
			old_name=`echo $file | sed 's/.bak//g'`
			mv $file $old_name
		done
		exit 1
	fi

	yum makecache &>/dev/null
	if [ $? -ne 0 ]; then
		echo "yum makecache failed!"
		exit 1
	fi
}

function check_install(){
	# check pkg install and uninstall
	cd /root/
	mkdir -p /root/check_result/success_log
	mkdir -p /root/check_result/failed_log
	echo "Checking pkg install is doing, please wait..."
	for pkg in $(cat /root/${pkglist})
	do
		echo "${pkg} is installing..."
		# get binary pkgs list
		cd /root/all_binary/$pkg/
		rpmlist=`cat rpmlist`
		yum install -y $rpmlist > install_res 2>&1
		# verify
	        if [ `cat install_res | grep "Complete!"` == "Complete!" ] &>/dev/null;then
			echo "${pkg} is installed successfully !!!"
			echo "$pkg" >> /root/check_result/succeed_install_pkglist
			mkdir -p /root/check_result/success_log/${pkg}
	 		mv install_res /root/check_result/success_log/${pkg}/
		else
			echo "${pkg} is installed failed !!!"
			echo "$pkg" >> /root/check_result/failed_install_pkglist
			mkdir -p /root/check_result/failed_log/${pkg}
			mv install_res /root/check_result/failed_log/${pkg}/
		fi
	done
	echo "Checking all pkg install have done !!!"
}

function check_function(){
	# function verify
	echo "Checking pkg function is doing, please wait..."
	for pkg in $(cat /root/${pkglist})
	do
		if [ -f /root/check_result/success_log/${pkg}/install_res ];then
			echo "verifying ${pkg} function..."
			cd /root/all_binary/$pkg/
			rpmlist=`cat rpmlist`
			function_list=$(rpm -ql $rpmlist | grep -E '/usr/s?bin')
			for function in $function_list
			do
				timeout 5 $function --help &> /dev/null || timeout 5 $function -h &> /dev/null || timeout 5 $function help &> /dev/null
				if [ $? -eq 0 ];then
					echo "verifying $function succeed!"
				else
					echo "verifying $function failed!"
					echo "$pkg [$function]" >> failed_function_list
				fi
			done
			
			if [ -f "failed_function_list" ];then
                                mkdir -p /root/check_result/failed_log/${pkg}
                                mv failed_function_list /root/check_result/failed_log/${pkg}/
                                echo "$pkg" >> /root/check_result/failed_function_pkglist
                        else
                                echo "$pkg" >> /root/check_result/succeed_function_pkglist
                        fi
		fi
	done
	echo "Checking all pkg function have done !!!"
}

function check_service(){
	# service verify
	echo "Checking pkg service is doing, please wait..."
	for pkg in $(cat /root/${pkglist})
	do
		if [ -f /root/check_result/success_log/${pkg}/install_res ];then
                        echo "verifying ${pkg} service..."
			cd /root/all_binary/$pkg/
			rpmlist=`cat rpmlist`
			service_list=$(rpm -ql $rpmlist | grep -E "\.service$" | awk -F "/" '{print $NF}')
			echo $service_list > service_list	
			service_id=0
			for service in $service_list
			do
				service_id=`expr $service_id + 1`
				service_res=""
				service_flag=true
				for action in "start" "status" "stop"
				do
					timeout 10 systemctl $action $service >> service_res 2>&1 
					if [ $? -ne 0 ];then
						echo "$pkg [$service]" >> failed_service_list
						service_flag=false
						break
					fi
				done
				
				if [ $service_flag = true ];then
					echo "verifying $service succeed!"
                                        mv service_res /root/check_result/success_log/${pkg}/service$service_id
				else
					echo "verifying $service failed!"
					mkdir -p /root/check_result/failed_log/${pkg}
					mv service_res /root/check_result/failed_log/${pkg}/service$service_id
				fi
			done
			
			if [ $service_id -eq 0 ];then
				echo "No service provides!"
			fi

			if [ -f "failed_service_list" ];then
				mv failed_service_list /root/check_result/failed_log/${pkg}/
				echo "$pkg" >> /root/check_result/failed_service_pkglist
			else
				echo "$pkg" >> /root/check_result/succeed_service_pkglist
			fi
		fi
	done
	echo "Checking all pkg service have done !!!"
}

function check_uninstall(){
	# uninstall
	echo "Checking pkg uninstall is doing, please wait..."
	for pkg in $(cat /root/${pkglist})
	do
		if [ -f /root/check_result/success_log/${pkg}/install_res ];then
			echo "${pkg} is uninstalling..."
			cd /root/all_binary/$pkg/
			rpmlist=`cat rpmlist`
			yum remove $rpmlist -y > uninstall_res 2>&1
			if [ `cat uninstall_res | grep "Complete!"` == "Complete!" ] &>/dev/null;then
				echo "${pkg} is uninstalled successfully !!!"
				echo "$pkg" >> /root/check_result/succeed_uninstall_pkglist
	 			mv uninstall_res /root/check_result/success_log/${pkg}/
			else
				echo "${pkg} is uninstalled failed !!!"
                                echo "$pkg" >> /root/check_result/failed_uninstall_pkglist
				mkdir -p /root/check_result/failed_log/${pkg}
                                mv uninstall_res /root/check_result/failed_log/${pkg}/
			fi
		fi
	done
	echo "Checking all pkg uninstall have done !!!"
}

check_file_and_dir
config_yum

pkglist=$1
check_install
check_function
check_service
check_uninstall
