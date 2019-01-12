FROM alpine

RUN apk add --update build-base imagemagick python3
RUN apk add python3-dev
RUN apk add zlib-dev
RUN apk add jpeg-dev

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY . /app
WORKDIR /app

CMD ["python3", "app.py"]
