#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="maintain",
    version="0.3.0",
    description="maintain",
    url="https://github.com/kylef/maintain",
    packages=find_packages(),
    package_data={},
    entry_points={
        "console_scripts": [
            "maintain = maintain.commands:cli",
        ]
    },
    install_requires=[
        "click",
        "semantic_version",
        "pyyaml",
        "commonmark==0.9.1",
        "gitpython",
        "jsonschema",
    ],
    author="Kyle Fuller",
    author_email="kyle@fuller.li",
    license="BSD",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: BSD License",
    ),
)
