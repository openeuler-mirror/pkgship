#!/bin/bash


source /etc/profile
source ~/.bash_profile
function check_process()
{
    PROCESS_NUM=`ps -ef | grep "pkgship-panel" | grep -v "grep" | wc -l`
    if [ $PROCESS_NUM -eq 0 ];then
        echo "Restart pkgship-panel" >> /var/log/pkgship/log_info.log
        pkgship-panel &
    fi
}

check_process