#!/usr/bin/env python

# from distutils.core import setup
import re
from setuptools import find_packages, setup

VERSION_FILE = "tweepy/__init__.py"
VERSION_REGEX = r"^__version__ = ['\"]([^'\"]*)['\"]"
with open(VERSION_FILE, "rt") as version_file:
    match = re.search(VERSION_REGEX, version_file.read(), re.M)

if match:
    version = match.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSION_FILE,))

tests_require = [
    "mock>=1.0.1",
    "nose>=1.3.3",
    "vcrpy>=1.10.3",
]

setup(name="tweepy",
      version=version,
      description="Twitter library for Python",
      license="MIT",
      author="Joshua Roesslein",
      author_email="tweepy@googlegroups.com",
      url="http://github.com/tweepy/tweepy",
      packages=find_packages(exclude=["tests", "examples"]),
      install_requires=[
          "PySocks>=1.5.7",
          "requests>=2.11.1",
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
      ],
      zip_safe=True)
