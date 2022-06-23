gunicorn: poetry run gunicorn osmcal.wsgi -b :8080 -w $GUNICORN_WOKERS -p /var/run/osmcal.pid --preload --access-logfile -

worker: poetry run ./manage.py process_tasks
