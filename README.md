# OpenStreetMap Calendar

A simple calendar for tracking OpenStreetMap related activities, so we don't have to wrestle the wiki anymore.

## Principles

* Less, but better.
* Work hard and be nice to people.

## User Documentation

Please look at [OpenStreetMap Calendar Documentation](https://osmcal.org/documentation/) for information about integration and API.

## Developer Documentation

This is a Django application, it uses [pipenv](https://pipenv.kennethreitz.org/en/latest/) for managing dependencies, install it with `pip3 install pipenv`. See their manual for more information.

We support Python ≥ 3.7 and PostgreSQL ≥ 10.

### Database

You need a running PostgreSQL database. There are two options: Running it locally or using Docker.

#### A) Local Installation
Create a PostgreSQL user called `osmcal` and a database `osmcal` with the owner set to `osmcal`. E.g.
```
CREATE ROLE osmcal WITH LOGIN ENCRYPTED PASSWORD 'postgres';
CREATE DATABASE osmcal OWNER osmcal;
CREATE EXTENSION postgis;
```

Make sure you have following line in your [pg_hba.conf](https://www.postgresql.org/docs/12/auth-pg-hba-conf.html), so osmcal need a password to log in:
```
local    all    all        trust
```
Alternatively, you can set your DB password using the `POSTGRES_PASSWORD` environment variable, c.f. the following section on Docker.




#### B) Docker

```
docker run -e POSTGRES_DB='osmcal' -e POSTGRES_USER='osmcal' -e POSTGRES_PASSWORD='postgres' --name osmcaldb postgis/postgis
```

*Note:* You can use `docker start osmcaldb` and `docker stop osmcaldb` after first run of the command above.

When using database in docker with the command above, the database host is:

```
export OSMCAL_PG_HOST=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' osmcaldb)
```

and database password is:

```
export OSMCAL_PG_PASSWORD='postgres'
```

### Virtual Environment

Use *pipenv* to create a virtual environment. Then, install the dependencies:

```
cd openstreetmap-calendar
pipenv install --dev
```

### Running Tests

```
pipenv run test
```

### Developer Server

If you need to use the login functionality locally, you need to create an OAuth app:

1. Go to osm.org -> My Settings -> oauth settings -> bottom of the page (My Client Applications) -> Register your application.
2. Fill `Name` and `Main Application URL`. No restrictions here.
3. You *must* fill `Callback URL` with `http://localhost:8000/oauth/callback`.
4. Mark `read their user preferences.`
5. Click `Register`.

When the application is registered on osm.org, set the respective environment variables used for oauth and copy *Consumer Key* and *Consumer Secret*:

```
export OSMCAL_OSM_KEY='...'
export OSMCAL_OSM_SECRET='...'
```

Then, you may run the database migration:

```
pipenv run migrate
```

and then the local server:

```
pipenv run devserver
```

If you need test data, you can load some using:

```
pipenv run ./manage.py osmcal/fixtures/demo.yaml
```

## API Documentation

The API is described using OpenAPI 3, the schema is located in `/api/schema/`. The currently live version is [visible here](https://osmcal.org/static/api.html).
