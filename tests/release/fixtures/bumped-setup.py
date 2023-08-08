#!/usr/bin/env python

from setuptools import setup

setup(
    name="changelog",
    version="1.0.0",
    url="https://github.com/kylef/changelog",
    author="Kyle Fuller",
    author_email="kyle@fuller.li",
    entry_points={
        "console_scripts": {
            "changelog = changelog:cli",
        }
    },
    install_requires=[
        "click",
        "semver",
        "commonmark",
    ],
    license="BSD",
)
