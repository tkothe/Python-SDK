AboutYou-Shop-SDK
=================

| **Author:** Arne Simon [arne.simon@silce-dice.de]
| **Version:** 0.3

A Python implementation for the AboutYou shop API.


Additional Conntacts
--------------------

iOS SDK
+++++++

* Jesse Hinrichsen [jesse@j-apps.com]
* Marius Schmeding [marius.schmeding@gmail.com]

Android SDK
+++++++++++

* Henning Dodenhof [Henning.dodenhof@4inchworks.de]


Installation
------------

Install the package via PIP::

    pip install aboutyou


Documentation
-------------

Documentation is found in HTML format in the *doc/build* sub-folder.


Endpoints
---------

- Staging
    http://ant-core-staging-s-api1.wavecloud.de/api
- Live
    http://ant-shop-api1.wavecloud.de/api


Change Log
----------

- 0.3:
    * Additional docmentation.
    * PyPI integration.
    * YAML configuration files.

- 0.2
    * Caching with Memcached and pylibmc.
    * EasyCollins has function, *getSimpleColors*.
    * Error handling fix.

- 0.1
    * Products return now there url to the mary+paul shop.
    * Dirty caching without memcached.
    * EasyCollins products are no bulk requests.
    * Extended documentation for EasyCollins.
