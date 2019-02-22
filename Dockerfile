FROM python:3-jessie as docstore

RUN apt-get update
RUN apt-get install --yes libimage-exiftool-perl libmagickwand-dev poppler-utils

RUN pip3 install pip==19.0.3

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

VOLUME ["/app"]
WORKDIR /app

ENV PORT 8072
EXPOSE 8072

COPY src /app
WORKDIR /app

CMD ["python3", "api.py", "/documents"]
