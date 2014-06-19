#!/usr/bin/env python
#from distutils.core import setup
import re
from setuptools import setup, find_packages
from pip.req import parse_requirements

VERSIONFILE = "tweepy/__init__.py"
ver_file = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, ver_file, re.M)

if mo:
    version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

install_reqs = parse_requirements('requirements.txt')
reqs = [str(req.req) for req in install_reqs]

setup(name="tweepy",
      version=version,
      description="Twitter library for python",
      license="MIT",
      author="Joshua Roesslein",
      author_email="tweepy@googlegroups.com",
      url="http://github.com/tweepy/tweepy",
      packages=find_packages(exclude=['tests']),
      install_requires=reqs,
      keywords="twitter library",
      zip_safe=True)
