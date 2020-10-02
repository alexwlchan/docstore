import os

import setuptools


def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))


def static_files(dirname):
    return [
        os.path.join(dirname, filename)
        for filename in os.listdir(local_file(f"src/docstore/{dirname}"))
    ]


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
    install_requires=[
        "attrs>=20.2.0",
        "cattrs>=1.0.0",
        "click>=7.1.2",
        "Flask>=1.1.2",
        "Pillow>=7.2.0",
        "scikit-learn>=0.23.2",
        "smartypants>=2.0.1",
        "Unidecode>=1.1.1",
        "wcag_contrast_ratio>=0.9",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "docstore = docstore.cli:main",
        ]
    },
)
