FROM ghcr.io/redocly/redoc/cli:v2.0.0-rc.72 AS apidocs

WORKDIR /docs

COPY osmcal/api/schema .
COPY Makefile .
RUN apk add make && redoc-cli bundle -o api.html --disableGoogleFont api.yaml

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y install curl make libgdal32
RUN curl -LO https://github.com/DarthSim/hivemind/releases/download/v1.1.0/hivemind-v1.1.0-linux-amd64.gz && gunzip hivemind-v1.1.0-linux-amd64.gz && mv hivemind-v1.1.0-linux-amd64 /usr/local/bin/hivemind && chmod +x /usr/local/bin/hivemind

RUN useradd -m osmcal
RUN chown osmcal /app

USER osmcal
RUN curl -sSL https://install.python-poetry.org | python3 -

# This is a hack to speed up docker builds through leveraging the layer cache.
COPY pyproject.toml poetry.lock Makefile ./
RUN make install

COPY . .
COPY --from=apidocs /docs/api.html osmcal/static/api.html
RUN make install staticfiles

EXPOSE 8080
CMD hivemind
