FROM python:3-jessie as docstore

RUN apt-get update
RUN apt-get install --yes libimage-exiftool-perl libmagickwand-dev poppler-utils

RUN pip3 install pip==19.0.3

# Strictly speaking we could just install straight from test_requirements.txt,
# but this lets us get the cached requirements.txt layer from the main app
# image if they've been built on the same machine.
COPY requirements.txt /
RUN pip3 install -r /requirements.txt
COPY test_requirements.txt /
RUN pip3 install -r /test_requirements.txt

COPY src /app
WORKDIR /app
