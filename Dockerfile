FROM python:3.6-jessie AS docstore

RUN apt-get update
RUN apt-get install --yes libimage-exiftool-perl libmagickwand-dev poppler-utils

RUN pip3 install pip==19.0.3

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

ENV PORT 8072
EXPOSE 8072

COPY src /app
WORKDIR /app

VOLUME ["/documents"]

ENTRYPOINT ["python3", "api.py", "/documents"]



FROM docstore AS tests

VOLUME ["/app"]
WORKDIR /app

COPY test_requirements.txt /
RUN pip3 install -r /test_requirements.txt



FROM tests AS pip_tools

RUN pip3 install pip-tools==3.4.0

ENTRYPOINT ["pip-compile"]
