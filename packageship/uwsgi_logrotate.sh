#!/bin/bash
UWSGI_PATH=/opt/pkgship/uwsgi
UWSGI_LOG_PATH=/var/log/pkgship-operation

function reopen_log_file() {
  old_log=${UWSGI_LOG_PATH}/uwsgi.log
  date_suffix=$(date -d "yesterday" +"%Y%m%d")
  new_log_zip=${UWSGI_LOG_PATH}/uwsgi-${date_suffix}.log.zip
  zip -q "${new_log_zip}" "${old_log}"

  rm -rf ${old_log}
  touch_file=${UWSGI_PATH}/.touch_for_logrotate
  touch "${touch_file}"
}

function delete_old_files() {
  max_count=31
  log_count=$(ls ${UWSGI_LOG_PATH} | wc -l)
  need_delete=$((log_count - max_count))

  if [ ${need_delete} -gt 0 ]; then
    need_delete_files=$(ls -rt ${UWSGI_LOG_PATH} | head -${need_delete})
    for file in ${need_delete_files}; do
      rm -rf ${UWSGI_LOG_PATH}/${file}
    done
  fi
}

while true; do
  sleep 1d
  reopen_log_file
  sleep 3s
  delete_old_files
done
