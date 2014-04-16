Caching
=======

Facets and Categories are always cached!
If you enable the extra caching Products and Variants will be also cached.

For caching is `pylibmc <http://sendapatch.se/projects/pylibmc/>`_ used.
To enable caching fill cache options in your configuration file.

.. code-block:: json

    {
        "entry_point_url" : "http://ant-core-staging-s-api1.wavecloud.de/api",
        "app_id": "",
        "app_token": "",
        "app_secret": "",
        "agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36",
        "image_url": "http://cdn.mary-paul.de/file/{}",
        "product_url": "",
        "cache": ["127.0.0.1"]
    }


Starting local Memcached
------------------------

.. code-block:: bash

    >>> memcached -d -m 512 -l 127.0.0.1 -p 11211 -u nobody

Check if is running:

.. code-block:: bash

    >>> ps -eaf | grep memcached
