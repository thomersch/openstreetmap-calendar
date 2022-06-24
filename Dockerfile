FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y install curl make libgdal28
RUN curl -LO https://github.com/DarthSim/hivemind/releases/download/v1.1.0/hivemind-v1.1.0-linux-amd64.gz && gunzip hivemind-v1.1.0-linux-amd64.gz && mv hivemind-v1.1.0-linux-amd64 /usr/local/bin/hivemind && chmod +x /usr/local/bin/hivemind

RUN useradd -m osmcal
RUN chown osmcal /app

USER osmcal
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# This is a hack to speed up docker builds through leveraging the layer cache.
COPY pyproject.toml poetry.lock Makefile ./
RUN make install

COPY . .
RUN make install staticfiles

EXPOSE 8080
CMD /app/run.sh
