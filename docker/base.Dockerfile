FROM python:3.6-jessie

RUN apt-get update
RUN apt-get install --yes \
  imagemagick \
  libimage-exiftool-perl \
  libmagickwand-dev \
  poppler-utils

RUN pip3 install --upgrade pip