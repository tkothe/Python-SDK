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

If you want to build the documentation yourself.

1. Checkout the git repo.
2. Go to the *doc/* folder.
3. make html


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
