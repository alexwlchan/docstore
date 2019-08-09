FROM alpine

RUN apk add --update \
    exiftool \
    imagemagick \
    imagemagick-dev \
    jpeg-dev \
    libmagic \
    poppler-utils \
    python3 \
    python3-dev \
    qpdf \
    zlib-dev && \
    rm -rf /var/cache/apk/*

RUN pip3 install --upgrade pip

COPY docker/install_github_dependency.sh /
RUN /install_github_dependency.sh get-mobi-cover-image 1795156
RUN /install_github_dependency.sh epub-thumbnailer dcdbd85
