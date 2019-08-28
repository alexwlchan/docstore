FROM alpine

RUN apk add --update \
    exiftool \
    imagemagick \
    imagemagick-dev \
    jpeg-dev \
    libmagic \
    poppler-utils \
    python3 \
    qpdf \
    zlib-dev && \
    rm -rf /var/cache/apk/*

# Install mimetype
RUN apk add --update apkbuild-cpan build-base perl perl-dev shared-mime-info && \
    PERL_MM_USE_DEFAULT=1 cpan File::BaseDir && \
    PERL_MM_USE_DEFAULT=1 cpan File::MimeInfo && \
    apk del apkbuild-cpan build-base perl-dev

RUN pip3 install --upgrade pip

COPY docker/install_github_dependency.sh /
RUN /install_github_dependency.sh get-mobi-cover-image 1795156
RUN /install_github_dependency.sh epub-thumbnailer dcdbd85
