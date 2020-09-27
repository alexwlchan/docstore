import os

import setuptools


def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


SOURCE = local_file("src")

setuptools.setup(
    name="docstore",
    version="2.0.0",
    author="Alex Chan",
    author_email="alex@alexwlchan.net",
    packages=setuptools.find_packages(SOURCE),
    package_data={
        "docstore": [
            "static/jquery.tagcloud.js",
            "static/natural_paper.png",
            "templates/_meta_info.html",
            "templates/index.html",
        ]
    },
    package_dir={"": SOURCE},
    url="https://github.com/alexwlchan/docstore",
    install_requires=[
        "attrs>=20.2.0",
        "cattrs>=1.0.0",
        "click>=7.1.2",
        "Flask>=1.1.2",
        "Pillow>=7.2.0",
        "requests>=2.24.0",
        "Unidecode>=1.1.1",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "docstore = docstore.cli:main",
        ]
    },
)
