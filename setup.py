#!/usr/bin/env python

import re
from setuptools import find_packages, setup

VERSION_FILE = "tweepy/__init__.py"
with open(VERSION_FILE) as version_file:
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                      version_file.read(), re.MULTILINE)

if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSION_FILE,))

with open("README.md") as readme_file:
    long_description = readme_file.read()

tests_require = [
    "mock>=1.0.1",
    "nose>=1.3.3",
    "vcrpy>=1.10.3",
]

setup(
    name="tweepy",
    version=version,
    description="Twitter library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Joshua Roesslein",
    author_email="tweepy@googlegroups.com",
    url="https://www.tweepy.org/",
    project_urls={
        "Documentation": "https://tweepy.readthedocs.io/",
        "Issue Tracker": "https://github.com/tweepy/tweepy/issues",
        "Source Code": "https://github.com/tweepy/tweepy",
    },
    download_url="https://pypi.org/project/tweepy/",
    packages=find_packages(exclude=["tests", "examples"]),
    install_requires=[
        "requests[socks]>=2.11.1",
        "requests_oauthlib>=0.7.0",
        "six>=1.10.0",
    ],
    tests_require=tests_require,
    extras_require={
        "dev": [
             "coveralls>=1.8.2",
             "tox>=2.4.0",
         ],
        "test": tests_require,
    },
    test_suite="nose.collector",
    keywords="twitter library",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    zip_safe=True,
)
