#!/usr/bin/env python
# -*- encoding: utf-8

import os
import subprocess
import zipfile

ROOT = subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"]).strip().decode("utf-8")

with zipfile.ZipFile(os.path.join(ROOT, "secrets.zip"), "w") as zf:
    for filename in ["docker_password.txt", "id_rsa", "id_rsa.pub"]:
        zf.write(os.path.join(ROOT, filename), arcname=filename)
