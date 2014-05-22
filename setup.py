from setuptools import setup
from pip.req import parse_requirements

import os

import aboutyou


BASE = os.path.dirname(__file__)


README = """
AboutYou-Shop-SDK
=================

| **Author:** Arne Simon [arne.simon@silce-dice.de]

A Python implementation for the AboutYou shop API.


Installation
------------

Install the package via PIP::

    pip install aboutyou


Quick Start
-----------

1. Modefiy one of the example config files.
2. Use the following lines::

  from aboutyou.config import YAMLConfig
  from aboutyou.easy import EasyAboutYou

  easy = EasyAboutYou(YAMLConfig('myconfig.yml'))
  cagtegoryforest = easy.categories()


Documentation
-------------

Documentation is found at http://aboutyou-shop-sdk.readthedocs.org/en/latest/.


Change Log
----------

- 0.3:
    * Additional docmentation.
    * Auto fetch flag.
    * PyPI integration.
    * YAML configuration files.

- 0.2:
    * Caching with Memcached and pylibmc.
    * EasyAboutYou has function, *getSimpleColors*.
    * Error handling fix.

- 0.1:
    * Products return now there url to the mary+paul shop.
    * Dirty caching without memcached.
    * EasyCollins products are no bulk requests.
    * Extended documentation for EasyAboutYou.
"""


# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(os.path.join(BASE, 'requirements.txt'))

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]


setup(
  name='aboutyou',
  packages=['aboutyou'],
  version=aboutyou.VERSION,
  install_requires=reqs,
  description='A connection to the aboutyou.de shop.',
  long_description=README,
  author='Arne Simon',
  author_email='arne.simon@slice-dice.de',
  license='MIT',
  url='https://bitbucket.org/slicedice/aboutyou-shop-sdk-python/overview',
  download_url='https://bitbucket.org/slicedice/aboutyou-shop-sdk-python/downloads',
  keywords=['aboutyou', 'shop', 'collins'],
  classifiers=[
    'Programming Language :: Python :: 2.7',
    'Topic :: Internet',
    'Topic :: Office/Business',
  ]
)
