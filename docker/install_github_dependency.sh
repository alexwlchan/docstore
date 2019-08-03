#!/usr/bin/env sh

set -o errexit
set -o nounset

apk add --update git

REPO="$1"
COMMIT="$2"

git clone "https://github.com/alexwlchan/$REPO.git" "/tools/$REPO"
cd "/tools/$REPO"
git checkout "$COMMIT"

apk del git
rm -rf /var/cache/apk/*
