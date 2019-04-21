#!/usr/bin/env python
# -*- encoding: utf-8
"""
Usage: release.py check_release_file
       release.py release
"""

import os
import subprocess
import sys

from releasetooling import check_release_file, configure_secrets, git, release, ROOT


if __name__ == '__main__':
    if (
        len(sys.argv) != 2 or
        sys.argv[1] in {"-h", "--help"} or
        sys.argv[1] not in {"check_release_file", "release"}
    ):
        print(__doc__.strip())
        sys.exit(1)

    configure_secrets()

    if sys.argv[1] == "release":
        new_version = release()
        subprocess.check_call(["make", "build"])
        subprocess.check_call([
            "docker", "tag",
            "docstore:latest", "greengloves/docstore:%s" % new_version
        ])

        try:
            subprocess.check_call([
                "docker", "login",
                "--username", "greengloves",
                "--password", open(os.path.join(ROOT, "docker_password.txt")).read().strip()
            ])
        except Exception:
            sys.exit(1)

        subprocess.check_call([
            "docker", "push", "greengloves/docstore:%s" % new_version
        ])

        git("remote", "add", "ssh-origin", "git@github.com:alexwlchan/docstore.git")
        git("push", "ssh-origin", "HEAD:master")
        git("push", "ssh-origin", "--tag")
    elif sys.argv[1] == "check_release_file":
        check_release_file()
    else:
        assert False, sys.argv
