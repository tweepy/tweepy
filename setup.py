#!/usr/bin/env python

import re
from setuptools import find_packages, setup

VERSIONFILE = "tweepy/__init__.py"
ver_file = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, ver_file, re.M)

if mo:
    version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in {}.".format(VERSIONFILE))

setup(name="tweepy",
      version=version,
      description="Twitter library for python",
      license="MIT",
      author="Joshua Roesslein",
      author_email="tweepy@googlegroups.com",
      url="http://github.com/tweepy/tweepy",
      packages=find_packages(exclude=['tests', 'examples']),
      install_requires=[
          "PySocks>=1.5.7",
          "requests>=2.11.1",
          "requests_oauthlib>=0.7.0",
      ],
      keywords="twitter library",
      python_requires=">=3.5",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Topic :: Software Development :: Libraries',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3 :: Only',
      ],
      zip_safe=True)
