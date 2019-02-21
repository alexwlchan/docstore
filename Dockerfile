FROM python:3-jessie as docstore

RUN apt-get update
RUN apt-get install --yes libimage-exiftool-perl libmagickwand-dev poppler-utils

RUN pip3 install --upgrade pip
RUN pip3 install preview-generator

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

VOLUME ["/documents"]

ENV PORT 8072
EXPOSE 8072

COPY src /app
WORKDIR /app

CMD ["python3", "api.py", "/documents"]



FROM docstore as docstore_test

COPY test_requirements.txt /
RUN pip3 install -r /test_requirements.txt



FROM docstore as docstore_piptools

RUN pip3 install pip-tools==3.4.0
