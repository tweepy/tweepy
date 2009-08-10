#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name="tweepy",
      version="1.0",
      description="Twitter library for python",
      license="MIT",
      author="Joshua Roesslein",
      author_email="tweepy@googlegroups.com",
      url="http://gitorious.org/tweepy",
      packages = find_packages(),
      keywords= "twitter wrapper library",
      zip_safe = True)
