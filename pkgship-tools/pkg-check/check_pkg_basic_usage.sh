#!/bin/bash
source /etc/pkgship-tools/check.config
init_path=$(pwd)

readonly NAME=$(basename $0)
ENABLE_INSTALL=0
ENABLE_FUNCTION=0
ENABLE_SERVICE=0
ENABLE_UNINSTALL=0
WITH_DOCKER=1

proj=""
pkglist=""

function parse_params(){
	if [ $# -eq 0 ] || [ "$1" = "-h" ]; then
		usage_help
		exit 0
	fi

	args=$(getopt -o iusfp:l: -al without-docker -- "$@")
	if [ $? -ne 0 ]; then
		    echo "Terminating..."
		    exit 1
	fi
	eval set -- "${args}"

	# While there is an another argument following "-p" or "-l", it is necessary to shift 2.
	while [ -n "$1" ]
	do
		case "$1" in
		-i) ENABLE_INSTALL=1; shift 1;;
		-u) ENABLE_UNINSTALL=1; shift 1;;
		-s) ENABLE_SERVICE=1; shift 1;;
		-f) ENABLE_FUNCTION=1; shift 1;;
		-p) proj=$2; shift 2;;
		-l) pkglist=$2; shift 2;;
		--without-docker) WITH_DOCKER=0; shift 1;;
		--) break;;
		*) echo "unknown args:${args}"
			usage_help
			exit 1
		esac
	done

}

function usage_help(){
	cat <<EOF
	Pkg Check Tool
	Usage:    sh ${NAME} [Options]
	Options:
	    -i
	        Enable to check install
	    -u
		Enable to check uninstall
	    -s
		Enable to check service
	    -f
		Enable to check function
	    -p project
		Specify the project name
	    -l package_list
		Specify the package list needed to check

EOF
}

# check  config
function check_config(){
	echo "Checking config, please wait..."
	if [ ! -f ${pkglist} ];then
		echo "package list file ${pkglist} does not exist!"
		exit 1
	fi

	# check osc env
	yum info installed osc &>/dev/null
	if [ $? -ne 0 ];then
		echo "osc is not installed!"
		exit 1
	fi

	osc search ${proj} | grep "matches for '${proj}' in projects" &>/dev/null
	if [ $? -ne 0 ];then
		echo "osc command excuted failed, please check:"
		echo "  1. osc config may be invalid"
		echo "  2. project ${proj} may not exist"
		exit 1
	fi
	# check obs REPO and ARCH
	osc ls -b ${proj} | grep "^${obs_repo}/${obs_arch}$" &>/dev/null
	if [ $? -eq 1 ];then
		echo "obs REPO or ARCH is not valid!"
		exit 1
	fi
	# check yum repo file
	if [ ! -f "${yum_repo}" ]; then
		echo "yum repo file doesn't exist!!"
		exit 1
	fi

	if [[ "${WITH_DOCKER}" -eq 1 ]]; then
		# check docker url
		echo "Downloading docker image, please wait..."
		wget ${docker_url}
		if [ $? -ne 0 ];then
			echo "downloading docker image source failed!"
			exit 1
		fi
	fi
}

# get binary rpm packages list
function get_binary(){
	proj=$1
	pkglist=$2

	rm -rf ${init_path}/check_result ${init_path}/all_binary
	mkdir ${init_path}/all_binary
	echo "Get binary packages lists is doing, please wait..."
	for pkg in $(cat ${pkglist})
	do	
		rpmlist=""
	        # get a list of compiled binary packages
		for rpm in $(osc ls -b ${proj} ${pkg} ${obs_repo} ${obs_arch} | grep '\.rpm$' | grep -v '.src.rpm' | grep -v 'debuginfo' | grep -v 'debugsource')
			do
				rpm=${rpm%\-*}
				rpmlist="${rpmlist} ${rpm}"
			done
		if [ -z ${rpmlist} ];then
			echo "Get ${pkg} binary packages list failed on obs server !!!"
			echo "Get ${pkg} binary packages list failed on obs server !!!" >> get_binary_failed
		else
			echo ${rpmlist} > rpmlist
			mkdir -p ${init_path}/all_binary/${pkg}
			mv rpmlist ${init_path}/all_binary/${pkg}
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
	rm ${docker_image_source} -f
        # clean previous docker env
	docker stop test_install &>/dev/null
	docker rm test_install &>/dev/null
    	# creat docker and cp files into docker env 
	docker run -itd --net=host --name=test_install --privileged=true ${docker_image_name} /usr/sbin/init &>/dev/null
	if [ $? -ne 0 ];then
		echo "creating docker failed!"
		exit 1
	fi
	# copy files into docker, will check files exist or not in script check_pkg_basic_usage_indocker.sh
	docker cp ${yum_repo} test_install:/root/
	docker cp ${init_path}/all_binary test_install:/root/
	docker cp ${init_path}/need_check_list test_install:/root/
	docker cp ${init_path}/check_pkg_basic_usage_indocker.sh test_install:/root/
	docker exec -it test_install bash -c 'echo "export TMOUT=0" >> /etc/bashrc && source /etc/bashrc 2>/dev/null && exit'
	docker restart test_install &>/dev/null
	echo "Create docker env completed !!!"
}

# start check
function main(){
	if [[ "${WITH_DOCKER}" -eq 1 ]]; then
		docker exec -it test_install /bin/bash -c "cd /root/ && bash check_pkg_basic_usage_indocker.sh ${ENABLE_INSTALL} ${ENABLE_FUNCTION} ${ENABLE_SERVICE} ${ENABLE_UNINSTALL} ${WITH_DOCKER}"
	elif [[ "${WITH_DOCKER}" -eq 0 ]]; then
		cd ${init_path}
		bash check_pkg_basic_usage_indocker.sh ${ENABLE_INSTALL} ${ENABLE_FUNCTION} ${ENABLE_SERVICE} ${ENABLE_UNINSTALL} ${WITH_DOCKER}
	fi
	if [ $? -eq 0 ];then
		if [[ "${WITH_DOCKER}" -eq 1 ]]; then
			# get result from docker, then clear temporary files and docker env
			docker cp test_install:/root/check_result ./
			docker stop test_install &>/dev/null
			docker rm test_install &>/dev/null
			echo "Clear docker env complete !!!"
		fi
		
		mv ${init_path}/get_binary_failed ${init_path}/check_result/ &>/dev/null
		mv ${init_path}/all_binary ${init_path}/check_result/
		rm -rf ${init_path}/need_check_list
		echo "Checking install and uninstall is complete, you can see log file in directory: ${init_path}/check_result, please backup check_result dir !!!"
	else
		rm -f ${init_path}/get_binary_failed
		rm -rf ${init_path}/all_binary
		rm -rf ${init_path}/need_check_list
		echo "Checking install and uninstall is failed! Please check the env!"
	fi
}

parse_params $@
echo "=============================================Begin============================================="
check_config
# $1 obs_proj_name $2 pkglist_file_name
get_binary ${proj} ${pkglist}

if [[ "${WITH_DOCKER}" -eq 1 ]]; then
	create_env
fi
main
echo "=============================================End==============================================="
