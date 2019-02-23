#!/usr/bin/env bash

set -o errexit
set -o nounset

ROOT=$(git rev-parse --show-toplevel)

python $(ROOT)/bin/index_document.py --port=8072 "$@"
