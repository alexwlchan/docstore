#!/usr/bin/env python
# -*- encoding: utf-8

import datetime as dt
import os
import re
import subprocess
import sys


def git(*args):
    """
    Run a Git command and check it completes successfully.
    """
    return subprocess.check_output(("git",) + args).strip().decode("utf-8")


ROOT = git("rev-parse", "--show-toplevel")


def tags():
    """
    Returns a list of all tags in the repo.
    """
    git("fetch", "--tags")
    all_tags = git("tag").splitlines()

    assert len(set(all_tags)) == len(all_tags)

    return set(all_tags)


def latest_version():
    """
    Returns the latest version, as specified by the Git tags.
    """
    versions = []

    for t in tags():
        assert t == t.strip()
        parts = t.split(".")
        assert len(parts) == 3, t
        parts[0] = parts[0].lstrip("v")
        v = tuple(map(int, parts))

        versions.append((v, t))

    _, latest = max(versions)

    assert latest in tags()
    return latest


def modified_files():
    """
    Returns a list of all files which have been modified between now
    and the latest release.
    """
    files = set()
    for command in [
        ['git', 'diff', '--name-only', '--diff-filter=d',
            latest_version(), 'HEAD'],
        ['git', 'diff', '--name-only']
    ]:
        diff_output = subprocess.check_output(command).decode('ascii')
        for l in diff_output.split('\n'):
            filepath = l.strip()
            if filepath:
                assert os.path.exists(filepath)
                files.add(filepath)
    return files


def has_source_changes():
    """
    Returns True if there are source changes since the previous release,
    False if not.
    """
    changed_files = [
        f for f in modified_files()
        if (f == "Dockerfile" or f.startswith("src"))
    ]
    print("*** Changed files: %s" % ", ".join(changed_files) or "<none>")
    return len(changed_files) != 0


RELEASE_FILE = os.path.join(ROOT, "RELEASE.md")


def has_release():
    """
    Returns True if there is a release file, False if not.
    """
    return os.path.exists(RELEASE_FILE)


RELEASE_TYPE = re.compile(r"^RELEASE_TYPE: +(major|minor|patch)")

MAJOR = "major"
MINOR = "minor"
PATCH = "patch"

VALID_RELEASE_TYPES = (MAJOR, MINOR, PATCH)


def parse_release_file():
    """
    Parses the release file, returning a tuple (release_type, release_contents)
    """
    with open(RELEASE_FILE) as infile:
        release_lines = list(infile)

    m = RELEASE_TYPE.match(release_lines[0])
    if m is not None:
        release_type = m.group(1)
        if release_type not in VALID_RELEASE_TYPES:
            print("Unrecognised release type %r" % (release_type,))
            sys.exit(1)
        del release_lines[0]
        release_contents = "".join(release_lines).strip()
    else:
        print(
            "RELEASE.md does not start by specifying release type. The first "
            "line of the file should be RELEASE_TYPE: followed by one of "
            "major, minor, or patch, to specify the type of release that "
            "this is (i.e. which version number to increment). Instead the "
            "first line was %r" % (release_lines[0],)
        )
        sys.exit(1)

    return release_type, release_contents


def check_release_file():
    if has_source_changes():
        if not has_release():
            print(
                "There are source changes but no RELEASE.md. Please create "
                "one to describe your changes."
            )
            sys.exit(1)
        parse_release_file()


def hash_for_name(name):
    return git("rev-parse", name)


def is_ancestor(a, b):
    check = subprocess.call(["git", "merge-base", "--is-ancestor", a, b])
    assert 0 <= check <= 1
    return check == 0


CHANGELOG_HEADER = re.compile(r"^## v\d+\.\d+\.\d+ - \d\d\d\d-\d\d-\d\d$")
CHANGELOG_FILE = os.path.join(ROOT, "CHANGELOG.md")


def changelog():
    with open(CHANGELOG_FILE) as i:
        return i.read()


def get_new_version(release_type):
    version = latest_version()
    version_info = [int(i) for i in version.lstrip("v").split(".")]

    new_version = list(version_info)
    bump = VALID_RELEASE_TYPES.index(release_type)
    new_version[bump] += 1
    for i in range(bump + 1, len(new_version)):
        new_version[i] = 0
    return tuple(new_version)


VERSION_PY = os.path.join(ROOT, "src", "version.py")


def get_new_version_string(release_type):
    new_version = get_new_version(release_type)
    return "v" + ".".join(map(str, new_version))


def update_changelog_and_version():
    contents = changelog()
    assert "\r" not in contents
    lines = contents.split("\n")
    assert contents == "\n".join(lines)
    for i, l in enumerate(lines):
        if CHANGELOG_HEADER.match(l):
            beginning = "\n".join(lines[:i])
            rest = "\n".join(lines[i:])
            assert "\n".join((beginning, rest)) == contents
            break

    release_type, release_contents = parse_release_file()

    new_version = get_new_version(release_type)
    new_version_string = get_new_version_string(release_type)

    print("New version: %s" % new_version_string)

    now = dt.datetime.utcnow()

    date = max([
        d.strftime("%Y-%m-%d") for d in (now, now + dt.timedelta(hours=1))
    ])

    heading_for_new_version = "## " + " - ".join((new_version_string, date))

    new_changelog_parts = [
        beginning.strip(),
        "",
        heading_for_new_version,
        "",
        release_contents,
        "",
        rest
    ]

    with open(CHANGELOG_FILE, "w") as o:
        o.write("\n".join(new_changelog_parts))

    # Update the version specified in version.py.  We"re looking to replace
    # a line of the form:
    #
    #       __version_info__ = (1, 2, 0)
    #
    lines = list(open(VERSION_PY))
    for idx, l in enumerate(lines):
        if l.startswith("__version_info__"):
            lines[idx] = "__version_info__ = (%d, %d, %d)\n" % new_version
            break
    else:  # no break
        raise RuntimeError("Never updated version in version.py?")

    with open(VERSION_PY, "w") as f:
        f.write("".join(lines))

    return release_type


def update_for_pending_release():
    release_type = update_changelog_and_version()

    git("rm", RELEASE_FILE)
    git("add", CHANGELOG_FILE)
    git("add", VERSION_PY)

    new_version = get_new_version_string(release_type)

    git(
        "commit",
        "-m", "Bump version to %s and update changelog\n\n[skip ci]" % new_version
    )
    git("tag", new_version)

    return new_version


def configure_secrets():
    git("config", "user.name", "Azure Pipelines on behalf of alexwlchan")
    git("config", "user.email", "azure@alexwlchan.fastmail.co.uk")

    print("SSH public key:")
    subprocess.check_call(["ssh-keygen", "-y", "-f", "id_rsa"])


def release():
    last_release = latest_version()

    print("Latest released version: %s" % last_release)

    HEAD = hash_for_name("HEAD")
    DEV_BRANCH = hash_for_name("origin/development")

    print("Current head:        %s" % HEAD)
    print("Current development: %s" % DEV_BRANCH)

    on_development = is_ancestor(HEAD, DEV_BRANCH)

    if not on_development:
        print("Trying to release while not on development?")
        sys.exit(1)

    if has_release():
        print("Updating changelog and version")
        new_version = update_for_pending_release()
    else:
        print("Not releasing due to no release file")
        sys.exit(0)

    print("Attempting a release.")

    return new_version


def branch_name():
    """Return the name of the branch under test."""
    # See https://graysonkoonce.com/getting-the-current-branch-name-during-a-pull-request-in-travis-ci/
    if os.environ['TRAVIS_PULL_REQUEST'] == 'false':
        return os.environ['TRAVIS_BRANCH']
    else:
        return os.environ['TRAVIS_PULL_REQUEST_BRANCH']
