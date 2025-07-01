[![Matrix](https://img.shields.io/matrix/osmcal:mustelo.de?server_fqdn=matrix.org&logo=matrix)](https://matrix.to/#/#osmcal:mustelo.de)

# OpenStreetMap Calendar

A simple, open calendar for tracking OpenStreetMap-related activities, such as mapping parties, hackathons, conferences, and other community events.

## Key Features

- **Open for Contributions**: Anyone with an OpenStreetMap account can add or manage events.
- **Multilingual Support**: Events and dates can be displayed in different languages based on user preferences.
- **RSS Feeds**: Subscribe to event feeds globally or by specific countries.

## Principles

* Less, but better.
* Work hard and be nice to people.

## User Documentation

For information on integration, using the API, or general usage, visit the [OpenStreetMap Calendar Documentation](https://osmcal.org/documentation/).

## Developer Documentation

The repo contains a [dev container](https://containers.dev) configuration, so you can develop without having to install all the dependencies on your machine manually. VS Code and PyCharm/IntelliJ have integrated support and you can even use Github Codespaces.

Alternatively you can install like any other Python/Django project. We're using [poetry](https://python-poetry.org) for managing dependencies. Please look at their documentation for installation instructions.

### Requirements

- Python ≥ 3.11
- PostgreSQL ≥ 15 with PostGIS

### Setup Instructions

1. **Clone the Repository**:  
   ```
   git clone https://github.com/<your-repo>/osmcal.git
   cd osmcal
   ```

2. **Install Dependencies**:  
   Use Poetry to install all necessary dependencies:  
   ```
   poetry install
   ```

3. **Configure the Database**:  
   Ensure a PostgreSQL database with PostGIS is available. If using the dev container, the database is automatically started. For manual setup, create an empty database named `osmcal`.

   Update the database settings in `osmcal/settings.py` if needed.

4. **Run Database Migrations**:  
   ```
   make migrate
   ```

5. **Start the Development Server**:  
   ```
   make devserver
   ```

6. **Load Test Data (Optional)**:  
   If needed, load sample data:  
   ```
   make fixtures
   ```

### Running Tests

To ensure everything is working correctly, run the tests:  
```
make test
```

### Mock Login for Development

During development, you can use a fake login without setting up OAuth. Scroll to the footer in debug mode and click "Mock login" to instantly log in as a normal user.

## API Documentation

The API is described using [OpenAPI 3](https://spec.openapis.org/oas/v3.0.0.html). The schema is located in `/api/schema/`. The live version is available [here](https://osmcal.org/static/api.html).

## Support and Contact

For questions, feedback, or support, feel free to reach out via the following channels:

- **Matrix Channel**: Join the discussion at [#osmcal:openstreetmap.org](https://matrix.to/#/#osmcal:mustelo.de).
- **GitHub Issues**: Report bugs or request features on the [issue tracker](https://github.com/thomersch/openstreetmap-calendar/issues).

## Contributing

We welcome contributions! Check out the developer documentation above for setup instructions, and feel free to submit pull requests or open issues. Translations can be found in the folder https://github.com/thomersch/openstreetmap-calendar/blob/master/osmcal/locale

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/thomersch/openstreetmap-calendar/blob/master/LICENSE) file for details.
