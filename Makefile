CALL := uv

GUNICORN_WORKERS ?= 1
FLY_REGION ?= ""
WRITABLE_REGION ?= ""
DEVSERVER_ARGS ?= ""

devserver:
	$(CALL) run ./manage.py runserver $(DEVSERVER_ARGS)

install:
	$(CALL) sync --no-dev --frozen

install-dev:
	$(CALL) sync --frozen

migrate:
	@if [ $(FLY_REGION) = $(WRITABLE_REGION) ]; then \
		$(CALL) run ./manage.py migrate;\
	else \
		echo "Running on non-writable node";\
	fi

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
