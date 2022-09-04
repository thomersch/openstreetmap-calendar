PATH := "$(PATH):$(HOME)/.local/bin"
CALL := env PATH=$(PATH) poetry

GUNICORN_WORKERS ?= 1

devserver:
	$(CALL) run ./manage.py runserver

install:
	$(CALL) install

dep-update:
	$(CALL) update

migrate:
	$(CALL) run ./manage.py migrate

makemigrations:
	$(CALL) run ./manage.py makemigrations

staticfiles:
	$(CALL) run ./manage.py collectstatic --noinput

gunicorn:
	$(CALL) run gunicorn osmcal.wsgi -b :8080 -w $(GUNICORN_WORKERS) --preload --access-logfile -

test:
	$(CALL) run ./manage.py test

fixtures:
	$(CALL) run ./manage.py loaddata osmcal/fixtures/demo.yaml

processtasks:
	$(CALL) run ./manage.py process_tasks

periodic:
	while true; do \
		echo "Running clearsessions" ;\
		$(CALL) run ./manage.py clearsessions ;\
		sleep 86400 ;\
	done;
