#!/usr/bin/env python

from setuptools import setup

with open("VERSION") as fp:
    VERSION = fp.read().strip()


setup(
    name="changelog",
    version=VERSION,
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
