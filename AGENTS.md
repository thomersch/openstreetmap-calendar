# Development environment

This project uses [devbox](https://www.jetify.com/devbox). `devbox shell` is
interactive-only and `devbox run --` doesn't reliably forward arbitrary
commands, so for non-interactive use (agents, scripts), load the devbox
environment into the current shell first:

eval "$(devbox shellenv)" && ./manage.py test osmcal.test_views

This puts `.venv/bin`, GDAL/GEOS, and postgres on PATH for the rest of the
command.
