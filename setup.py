#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='maintain',
    version='0.1.0',
    description='maintain',
    url='https://github.com/kylef/maintain',
    packages=find_packages(),
    package_data={
    },
    entry_points={
        'console_scripts': [
            'maintain = maintain:cli',
        ]
    },
    install_requires=[
        'click',
    ],
    author='Kyle Fuller',
    author_email='kyle@fuller.li',
    license='BSD',
    classifiers=(
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.2',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'License :: OSI Approved :: BSD License',
    )
)

