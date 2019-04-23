#!/usr/bin/env python
# -*- encoding: utf-8
"""
A quick 'n' dirty script for uploading a bunch of payslips into docstore.

You don't want to use this script directly, but it might be useful the next
time you want to do a bulk import.
"""

import datetime as dt
import os

import requests

auth = ("username", "password")

base_url = "https://docstore.example.org"

for f in sorted(os.listdir(".")):
    if not f.endswith(".pdf"):
        continue

    print(f)
    month = dt.datetime.strptime(f, "Print Payslip %Y-%m.pdf")
    title = month.strftime("%Y-%m: Payslip for %b %Y")

    resp = requests.post(
        f"{base_url}/upload",
        data={
            "title": title,
            "filename": f,
            "tags": "employer:wellcome"
        },
        files={"file": open(f, "rb")},
        auth=auth
    )
    resp.raise_for_status()

    doc_id = resp.json()["id"]
    resp = requests.get(f"{base_url}/documents/{doc_id}", auth=auth)
    resp.raise_for_status()

    url = os.path.join(f"{base_url}/files", resp.json()["file_identifier"])
    resp = requests.get(url, stream=True, auth=auth)
    resp.raise_for_status()
    stored_data = resp.raw.read()
    original_data = open(f, "rb").read()

    if original_data == stored_data:
        os.unlink(f)
