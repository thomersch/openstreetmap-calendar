CALL="poetry"

devserver:
	$(CALL) run ./manage.py runserver

install:
	$(CALL) install

dep-update:
	$(CALL) update

migrate:
	$(CALL) run ./manage.py migrate

staticfiles:
	$(CALL) run ./manage.py collectstatic --noinput

gunicorn:
	gunicorn osmcal.wsgi

test:
	$(CALL) run ./manage.py test

fixtures:
	$(CALL) run ./manage.py osmcal/fixtures/demo.yaml
