FROM python:3.6-jessie

RUN apt-get update && \
  apt-get install --yes \
  imagemagick \
  libimage-exiftool-perl \
  libmagickwand-dev \
  poppler-utils \
  qpdf

RUN pip3 install --upgrade pip

RUN git clone https://github.com/alexwlchan/get-mobi-cover-image.git /tools/get-mobi-cover-image && \
    cd /tools/get-mobi-cover-image && \
    git checkout 1795156

RUN git clone https://github.com/alexwlchan/epub-thumbnailer.git /tools/epub-thumbnailer && \
    cd /tools/epub-thumbnailer && \
    git checkout dcdbd85
