#!/bin/sh
source web/bin/activate

truncate -s 0 nohup.out
truncate -s 0 celery.out
truncate -s 0 celery_beat.out

nohup gunicorn -w 4 -b 127.0.0.1:5000 --access-logfile web_access.log main:flask_app &
nohup celery -A main worker -P gevent -l INFO > celery.out &
nohup celery -A main beat -l INFO > celery_beat.out &

sleep 1

echo "所有nohup任务已启动并在后台运行。"

exit 0