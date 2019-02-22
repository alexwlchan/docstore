FROM python:3-jessie as docstore

RUN apt-get update
RUN apt-get install --yes libimage-exiftool-perl libmagickwand-dev poppler-utils

RUN pip3 install pip==19.0.3
RUN pip3 install pip-tools==3.4.0
