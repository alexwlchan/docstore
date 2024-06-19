import functools
import os
import subprocess


@functools.lru_cache()
def current_commit() -> str:
    """
    Returns the commit of the current docstore version.
    """
    return (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=os.path.dirname(os.path.abspath(__file__))
        )
        .strip()
        .decode("utf8")[:7]
    )
