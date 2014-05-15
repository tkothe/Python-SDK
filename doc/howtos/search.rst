Search
======

One of the most likely things you will do with the Aboutyou-API is to search.
So here are some more extensive examples to make your self familiar with the
Python version of the Aboutyou-API-SDK. Have Fun :)


with Aboutyou
-------------

.. code-block:: python
    :linenos:

    from aboutyou import JSONConfig, Aboutyou

    aboutyou = Aboutyou(JSONConfig("my-config.json"))

    # get all products in categorie 16354 back
    response = aboutyou.productsearch("testsession", filter={"categories":[16354]})

    print response["product_count"]


with EasyAboutyou
-----------------

.. code-block:: python
    :linenos:

    from aboutyou.easy import EasyAboutYou
    from aboutyou import JSONConfig

    easy = EasyAboutYou(JSONConfig("my-config.json"))

