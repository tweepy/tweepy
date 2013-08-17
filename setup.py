#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages
from tweepy import __version__
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt')
reqs = [str(req.req) for req in install_reqs]

setup(name="tweepy",
      version=__version__,
      description="Twitter library for python",
      license="MIT",
      author="Joshua Roesslein",
      author_email="tweepy@googlegroups.com",
      url="http://github.com/tweepy/tweepy",
      packages=find_packages(exclude=['tests']),
      intall_requires=reqs,
      keywords="twitter library",
      zip_safe=True)
