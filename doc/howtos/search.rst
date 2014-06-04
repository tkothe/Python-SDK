Search
======

One of the most likely things you will do with the Aboutyou-API is to search.
So here are some more extensive examples to make your self familiar with the
Python version of the Aboutyou-API-SDK. Have Fun :)


with Aboutyou
-------------

.. code-block:: python
    :linenos:

    from aboutyou.config import JSONConfig
    from aboutyou.api import Aboutyou

    aboutyou = Aboutyou(JSONConfig("my-config.json"))

    # get all products in categorie 16354 back
    response = aboutyou.productsearch("testsession", filter={"categories":[16354]})

    print response["product_count"]


with EasyAboutyou
-----------------

.. code-block:: python
    :linenos:

    from aboutyou.easy import EasyAboutYou
    from aboutyou.config import JSONConfig

    easy = EasyAboutYou(JSONConfig("my-config.json"))


Search for Colors in Categories
-------------------------------

.. code-block:: python
    :linenos:

    result = easy.search(TEST_SESSION, filter={"categories":[19631, 19654],
                                               "facets":{FACET.COLOR: [1,9]}
                                                     })
    with codecs.open("dump.txt", "w", encoding="utf8") as o:
        for p in result.products:
            o.write(u"{} {} {}\n".format(p.id, p.name, p.active))
            for v in p.variants:
                # o.write(u"{}".format(v.obj))
                o.write(u"    {} {}\n".format(v.id, v.quantity))
                o.write(u"        {}\n".format([ (f.facet_id, f.name) for f in v.attributes["color"]]))