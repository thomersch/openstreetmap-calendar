# OpenStreetMap Calendar

A simple calendar for tracking OpenStreetMap related activities, so we don't have to wrestle the wiki anymore.

## Principles

* Less, but better.
* Work hard and be nice to people.

## User Documentation

Please look at [OpenStreetMap Calendar Documentation](https://osmcal.org/documentation/) for information about integration and API.

## Developer Documentation

This is a Django application, it uses [poetry](https://python-poetry.org) for managing dependencies. Please look at their documentation for installation instructions.

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

Use *poetry* to create a virtual environment. Then, install the dependencies:

```
cd openstreetmap-calendar
poetry install
```

### Running Tests

```
poetry run ./manage.py test
```

### Developer Server

In order to facilitate testing, you can use a fake login locally without having to setup OAuth first. To do this, scroll down to the footer. In debug mode, there is a link called "Mock login" which will instantly log you in as a normal user.

To prepare for application launch run the database migrations:

```
poetry run ./manage.py migrate
```

and then the local server:

```
poetry run ./manage.py runserver
```

If you need test data, you can load some using:

```
poetry run ./manage.py loaddata osmcal/fixtures/demo.yaml
```

## API Documentation

The API is described using OpenAPI 3, the schema is located in `/api/schema/`. The currently live version is [visible here](https://osmcal.org/static/api.html).

## OAuth Setup

If want to test the OAuth flow, you need to create an OAuth app first:

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
