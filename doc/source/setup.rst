Setup
=====

Software Requirements
---------------------

.. note::

    These software packages are only required if you want to use caching.

* `Memcached <http://memcached.org/>`_
* `pylibmc <http://sendapatch.se/projects/pylibmc/>`_

Start Memcached
---------------

Starting Memcached with:

.. code-block:: bash

    memcached -d -m 512 -l 127.0.0.1 -p 11211 -u nobody

+ d: tells Memcached to run as a daemon
+ m: the memory (Memcached uses actual memory and not disk memory)
+ l: where to listen, here would only listen for local requests, if you want to allow other computers to access Memcached, specify the external IP
+ p: the port, default 11211
+ u: the user to run as


Connecting in Python:

.. code-block:: python

    >>> import pylibmc

    >>> mc = pylibmc.Client(["127.0.0.1"], binary=True,
                       behaviors={"tcp_nodelay": True,
                       "ketama": True})

    >>> mc["some_key"] = "Some value"
    >>> mc["some_key"]
    'Some value'
    >>> del mc["some_key"]
    >>> "some_key" in mc
    False

    >>> mc.set("some_key", "Some value")
    True
    >>> value = mc.get("some_key")
    >>> value
    'Some value'
    >>> mc.set("another_key", 3)
    True
    >>> mc.delete("another_key")
    True
