# OpenStreetMap Calendar

A simple calendar for tracking OpenStreetMap-related activities.

## Principles

* Less, but better.
* Work hard and be nice to people.

## User Documentation

Please look at [OpenStreetMap Calendar Documentation](https://osmcal.org/documentation/) for information about integration and API.

## Developer Documentation

The repo contains a [dev container](https://containers.dev) configuration, so you can develop without having to install all the dependencies on your machine manually. VS Code and PyCharm/IntelliJ have integrated support and you can even use Github Codespaces.

We also feature a [devbox](https://www.jetify.com/devbox) setup which allows to setup a development environment without having to utilize Docker and containers. `devbox services up` allows you to start the project itself and its dependencies.

Alternatively you can install like any other Python/Django project. We're using [uv](https://docs.astral.sh/uv/) for managing dependencies. Please look at their documentation for installation instructions.

We support Python ≥ 3.11 and PostgreSQL ≥ 15. (Older versions might work, but no guarantees).

### Database

You need a running PostgreSQL database with PostGIS installed. If you're using the dev container, the DB is automatically started and set up.

If you set this up manually, make sure you have an empty DB before starting. By default we're using the `osmcal` for user and DB with no password set. For more details, check `osmcal/settings.py`.

### Running Tests

```
make test
```

### Developer Server

In order to facilitate testing, you can use a fake login locally without having to setup OAuth first. To do this, scroll down to the footer. In debug mode, there is a link called "Mock login" which will instantly log you in as a normal user.

To prepare for application launch run the database migrations:

```
make migrate
```

and then the local server:

```
make devserver
```

If you need test data, you can load some using:

```
make fixtures
```

## API Documentation

The API is described using OpenAPI 3, the schema is located in `/api/schema/`. The currently live version is [visible here](https://osmcal.org/static/api.html).
