#!/bin/bash
REPO_CONFIG_FILE="/etc/yum.repos.d/pkgship_elasticsearch.repo"
INSTALL_SOFTWARE=$1

function check_es_status() {
  visit_es_response=$(curl -s -XGET http://127.0.0.1:9200)
  if [[ "${visit_es_response}" =~ "You Know, for Search" ]]; then
    echo "[ERROR] The service is running, please close it manually and try again."
    exit 1
  fi
}

function create_es_repo() {
  echo "[INFO] Start to create ES official installation repo"

  if [ ! -f ${REPO_CONFIG_FILE} ]; then
    touch ${REPO_CONFIG_FILE}
  fi
  echo "[pkgship_elasticsearch]
name=Elasticsearch repository for 7.x packages
baseurl=https://artifacts.elastic.co/packages/7.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md" >${REPO_CONFIG_FILE}
  # create repo file failed
  if [ ! -f ${REPO_CONFIG_FILE} ]; then
    echo "[ERROR] pkgship_elasticsearch.repo file creation failed!"
    echo "Please confirm whether you have permission!"
    exit 1
  fi

  echo "[INFO] Create ES repo success"
}

function download_install_es() {
  echo "[INFO] start to download and install elasticsearch"
  # check repo
  es_repo=$(yum repolist | grep "pkgship_elasticsearch")
  if [ -z "${es_repo}" ]; then
    echo "[ERROR] not found elasticsearch repo,please check config file in /etc/yum.repos.d"
    exit 1
  fi

  yum install elasticsearch-7.10.1 -y

  if [ $? -ne 0 ]; then
    echo "[ERROR] install elasticsearch failed"
    exit 1
  fi

  echo "[INFO]download and install elasticsearch success"
}

function change_elasticsearch_login_type() {
  echo "[INFO] start to modify the elasticsearch user login method"

  elasticsearch_user_config=$(cat /etc/passwd | grep "elasticsearch")
  if [ -z "${elasticsearch_user_config}" ]; then
    echo "[ERROR] elasticsearch user not exists,please check elasticsearch Installation status"
  fi

  sed -i 's/elasticsearch\ user:\/nonexistent:\/sbin\/nologin/elasticsearch\ user:\/nonexistent:\/bin\/bash/g' /etc/passwd

  if [ $? -ne 0 ]; then
    echo "[ERROR] failed to modify the elasticsearch user login method,please check /etc/passwd"
    exit 1
  fi

  echo "[INFO] modify the elasticsearch user login method success"
}

function change_elasticsearch_file_owner() {
  chown -R elasticsearch: /usr/share/elasticsearch/
  chown -R elasticsearch: /etc/sysconfig/elasticsearch
  chown -R elasticsearch: /etc/elasticsearch
  chown -R elasticsearch: /var/log/elasticsearch
  chown -R elasticsearch: /var/lib/elasticsearch
}

function start_elasticsearch_service() {
  echo "[INFO] start to start elasticsearch service"
  su - elasticsearch -c "/bin/bash /usr/share/elasticsearch/bin/elasticsearch &" >/dev/null 2>&1

  for i in {1..12}; do
    visit_es_response=$(curl -s -XGET http://127.0.0.1:9200)
    if [[ "${visit_es_response}" =~ "You Know, for Search" ]]; then
      echo "[INFO] elasticsearch start success"
      exit 0
    fi
    sleep 5
  done

  echo "[ERROR] elasticsearch start failed,please check /var/log/elasticsearch/elasticsearch.log"
  exit 1
}

function download_install_redis() {
  echo "[INFO] start to download and install redis"

  yum install redis -y

  if [ $? -ne 0 ]; then
    echo "[ERROR] download and install redis failed"
    echo "[ERROR] Please check the files under the /etc/yum.repos.d/ is configed correct"
    exit 1
  fi

  echo "[INFO]download and install Redis success"
  echo "[INFO]Start the redis service"
  redis-server --daemonize yes
  if [ $? -ne 0 ]; then
    echo "[ERROR] Start the redis service failed, Please start the service manually"
    exit 1
  fi
  echo "[INFO]Start the Redis service success"
}

function main() {
  if [ "${INSTALL_SOFTWARE}" = "elasticsearch" ]; then
    check_es_status
    create_es_repo
    download_install_es
    change_elasticsearch_login_type
    change_elasticsearch_file_owner
    start_elasticsearch_service
  elif [ "${INSTALL_SOFTWARE}" = "redis" ]; then
    download_install_redis
  else
    echo "Failed to parse parameters, please use 'bash auto_install_es.sh elasticsearch/redis' "
    exit 1
  fi
}
main
