Usage
=====

.. contents::


Configuration
-------------

The SDK has to be configured for your connection. The SDK comes with four
instances:

    * :py:class:`aboutyou.Config`
    * :py:class:`aboutyou.YAMLConfig`
    * :py:class:`aboutyou.JSONConfig`
    * :py:class:`aboutyou.JSONEnvironmentFallbackConfig`


A good practice is to use the YAMLConfig instance, so your app-id and password
are not hard coded in the source code and YAML provides a nice and user-friendly
data layout.

Simple Setup
++++++++++++

You just want the API working and have no special needs.
Then use the :py:class:`aboutyou.Config` class direktly.

.. code-block:: python
    :linenos:

    from aboutyou import Config, Aboutyou

    config = Config(app_id=101, app_token="<yourtoken>")
    client = Aboutyou(config)

    tree = client.categorytree()

This mayby a good setup for testing and getting used to the API, but not wise
for production enviroumnet.

A Real Life Setup
+++++++++++++++++

.. code-block:: python
    :linenos:

    from aboutyou import YAMLConfig
    from aboutyou.easy import EasyAboutYou

    easy = EasyAboutYou(YAMLConfig('myconfig.yml'))


Getting the Brand
-----------------

.. code-block:: python
    :linenos:

    p = easy.producstById([239982])[0]

    print p.name

    for v in p.variants:
        print v.id
        print [f.name for f in v.attributes["brand"]]


Many products by id
--------------------

If you want to get products directly by its id.

.. code-block:: python
    :linenos:

    from aboutyou import YAMLConfig
    from aboutyou.easy import EasyAboutYou, SearchException

    easy = EasyAboutYou(YAMLConfig("myconfig.yaml"))

    try:
        for p in easy.productsById([237188, 237116]):
            print p.name
    except SearchException as e:
        print e.withError   # list of tuples (id, [errors]) for not found products
        print e.found       # list of found products


Search for Colors in Categories
-------------------------------

.. code-block:: python
    :linenos:

    result = easy.search(TEST_SESSION, filter={"categories":[19631, 19654],
                                               "facets":{Constants.FACET_COLOR: [1,9]}
                                                     })
    with codecs.open("dump.txt", "w", encoding="utf8") as o:
        for p in result.products:
            o.write(u"{} {} {}\n".format(p.id, p.name, p.active))
            for v in p.variants:
                # o.write(u"{}".format(v.obj))
                o.write(u"    {} {}\n".format(v.id, v.quantity))
                o.write(u"        {}\n".format([ (f.facet_id, f.name) for f in v.attributes["color"]]))


Category Tree
-------------

.. code-block:: python
    :linenos:

    from aboutyou.easy import EasyAboutYou
    from aboutyou import JSONConfig

    easy = EasyCollins(JSONConfig('myconfig.json'))

    # all categories of the first level
    for c in easy.categories():
        print '---', c.name, '---'
        for sub in c:
            print sub.name

    damen = easy.categoryByName("Damen")

    print damen.id, damen.name

