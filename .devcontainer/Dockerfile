FROM python:3.11

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y install curl make libgdal32
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

CMD /bin/bash
