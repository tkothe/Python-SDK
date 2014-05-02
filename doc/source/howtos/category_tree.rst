Category Tree
-------------

.. code-block:: python
    :linenos:

    from collins.easy import EasyCollins
    from collins import JSONConfig

    easy = EasyCollins(JSONConfig('slice-dice-config.json'))

    # all categories of a level
    for c in easy.categories():
        print '---', c.name, '---'
        for sub in c:
            print sub.name

    damen = easy.categoryByName("Damen")

    print damen.id, damen.name
