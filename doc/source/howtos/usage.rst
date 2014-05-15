Usage
=====

Brand?
------

.. code-block:: python

    p = easy.producstById([239982])[0]

    print p.name

    for v in p.variants:
        print v.id
        print [f.name for f in v.attributes["brand"]]


Many products by id
--------------------

.. code-block:: python

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

    result = easy.search(TEST_SESSION, filter={"categories":[19631, 19654],
                                               "facets":{Constants.FACET_COLOR: [1,9]}
                                                     }, result={})
    with codecs.open("dump.json", "w", encoding="utf8") as o:
        for p in result.products:
            o.write(u"{} {} {}\n".format(p.id, p.name, p.active))
            for v in p.variants:
                # o.write(u"{}".format(v.obj))
                o.write(u"    {} {}\n".format(v.id, v.quantity))
                o.write(u"        {}\n".format([ (f.facet_id, f.name) for f in v.attributes["color"]]))

