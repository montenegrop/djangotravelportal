#!/bin/bash
source .sourceenv
TEMP_DBNAME=yas-$(date +%F).sql
ssh yas_test "mysqldump -P ${REMOTE_DB_PORT} -u ${REMOTE_DB_USER} -p${REMOTE_DB_PASSWORD} ${REMOTE_DB_NAME} > ${TEMP_DBNAME}"
ssh yas_test "gzip ${TEMP_DBNAME}"
scp yas_test:/home/juan/${TEMP_DBNAME}.gz .
RESULT=$?
if [ $RESULT -eq 0 ]; then
    mysql -P ${DB_PORT} -u ${DB_USER} -p${DB_PASSWORD} -h ${DB_HOST} ${DB_NAME} -e "DROP database ${DB_NAME};"
    mysql -P ${DB_PORT} -u ${DB_USER} -p${DB_PASSWORD} -h ${DB_HOST} -e "CREATE database ${DB_NAME} COLLATE 'utf8_unicode_ci';"
    gunzip ${TEMP_DBNAME}
    mysql -P ${DB_PORT} -u ${DB_USER} -p${DB_PASSWORD} -h ${DB_HOST} ${DB_NAME} < ${TEMP_DBNAME}
else
  echo "failed"
fi
