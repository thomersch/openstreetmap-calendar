FROM python:3.11

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y install curl make libgdal32
RUN pip install poetry==1.7.1
