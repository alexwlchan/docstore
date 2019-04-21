#!/usr/bin/env python
# -*- encoding: utf-8
"""
Usage: release.py check_release_file
       release.py release
"""

import subprocess
import sys

from releasetooling import check_release_file, configure_secrets, git, release


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
        subprocess.check_call([
            "docker", "push", "greengloves/docstore:%s" % new_version
        ])
        git("push", "ssh-origin", "HEAD:master")
        git("push", "ssh-origin", "--tag")
    elif sys.argv[1] == "check_release_file":
        check_release_file()
    else:
        assert False, sys.argv
