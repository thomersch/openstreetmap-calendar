# OpenStreetMap Calendar

A simple calendar for tracking OpenStreetMap related activities, so we don't have to wrestle the wiki anymore.

## Principles

* Less, but better.
* Work hard and be nice to people.

## User Documentation

Please look at [OpenStreetMap Calendar Documentation](https://osmcal.org/documentation/) for information about integration and API.


# Developer Documentation

This is a Django application, it uses [pipenv](https://pipenv.kennethreitz.org/en/latest/) for managing dependencies, install it with `pip3 install pipenv`. See their manual for more information.

## Database

You need running Postgres database. There are two options:

- Run a Postgres database locally. For database, use:

    - database name: `osmcal`
    - user name: `osmcal`
    - password: `postgres`

    **Note:** You may use any password you want. However, you always need to specify the environment variable `POSTGRES_PASSWORD` before run *test* or *server*:

    ```
    export POSTGRES_PASSWORD='postgres'
    ```

    When using local database, the database host is *localhost*:

    ```
    export OSMCAL_PG_HOST='localhost'
    ```

- Use docker image:

    ```
    docker run -e POSTGRES_DB='osmcal' -e POSTGRES_USER='osmcal' -e POSTGRES_PASSWORD='postgres' --name osmcaldb postgis/postgis
    ```

    **Note:** It's ok to just `docker start osmcaldb` and `docker stop osmcaldb` after first run of the command above.

    When using database in docker with the command above, the database host is:

    ```
    export OSMCAL_PG_HOST=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' osmcaldb)
    ```

    and database password is:

    ```
    export OSMCAL_PG_PASSWORD='postgres'
    ```

## Virtual environment

Use *pipenv* to create virtual environment. Then, install requirements:

```
cd openstreetmap-calendar
pipenv install
```

## Unit tests

When the database is running and the local variables `OSMCAL_PG_HOST` and `OSMCAL_PG_PASSWORD` are set, you may run tests:

```
pipenv run test
```

## Developer server

When database is running and the local variables `OSMCAL_PG_HOST` and `OSMCAL_PG_PASSWORD` are set, you need to set the OpenStreetMap oauth environment variables:

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
