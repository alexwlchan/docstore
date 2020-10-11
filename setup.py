import os

import setuptools


def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


def static_files(dirname):
    return [
        os.path.join(dirname, filename)
        for filename in os.listdir(local_file(f"src/docstore/{dirname}"))
    ]


with open(local_file("requirements.txt")) as f:
    INSTALL_REQUIRES = list(f)


SOURCE = local_file("src")

setuptools.setup(
    name="docstore",
    version="2.0.0",
    author="Alex Chan",
    author_email="alex@alexwlchan.net",
    packages=setuptools.find_packages(SOURCE),
    package_data={"docstore": static_files("static") + static_files("templates")},
    package_dir={"": SOURCE},
    url="https://github.com/alexwlchan/docstore",
    install_requires=INSTALL_REQUIRES,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "docstore = docstore.cli:main",
        ]
    },
)
