#!/usr/bin/env python
# -*- encoding: utf-8

import sys

import requests


requests.post(
    "http://localhost:5042/api/documents",
    json={"path": sys.argv[1], "title": sys.argv[2], "tags": sys.argv[3:]}
)
