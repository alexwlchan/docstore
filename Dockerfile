FROM python:3-jessie

RUN apt-get update
RUN apt-get install --yes libimage-exiftool-perl libmagickwand-dev poppler-utils

RUN pip3 install preview-generator

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY src /app
WORKDIR /app

VOLUME ["/documents"]

ENV PORT 8072
EXPOSE 8072

CMD ["python3", "api.py", "/documents"]
