FROM python:3-jessie

RUN apt-get update
RUN apt-get install --yes libimage-exiftool-perl libmagickwand-dev poppler-utils

RUN pip3 install preview-generator

WORKDIR "/data"
VOLUME ["/data"]

COPY create_thumbnail.py /
ENTRYPOINT ["python3", "/create_thumbnail.py"]
