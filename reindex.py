#!/usr/bin/env python
# -*- encoding: utf-8

import requests

resp = requests.get("http://localhost:8072/api/trigger_reindex")
resp.raise_for_status()
print(resp.json())
