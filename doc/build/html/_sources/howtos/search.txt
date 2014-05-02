Search
======

One of the most likely things you will do with the Collins-API is to search.
So here are some more extensive examples to make your self familiar with the
Python version of the Collins-API-SDK. Have Fun :)


with Collins
------------

.. code-block:: python
    :linenos:

    from collins import JSONConfig, Collins

    collins = Collins(JSONConfig("my-config.json"))

    # get all products in categorie 16354 back
    response = collins.productsearch("testsession", filter={"categories":[16354]})

    print response["product_count"]


with EasyCollins
----------------

.. code-block:: python
    :linenos:

    from collins.easy import EasyCollins
    from collins import JSONConfig

    easy = EasyCollins(JSONConfig("my-config.json"))

