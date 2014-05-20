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

If plan to go in production, you want a little more controle over whats going on.
Which leads to more configuration you do not want to have directly in your code.

Here is an example of how to use the YAML configuration file.

.. code-block:: python
    :linenos:

    from aboutyou import YAMLConfig
    from aboutyou.easy import EasyAboutYou

    easy = EasyAboutYou(YAMLConfig('myconfig.yml'))

    print easy.config.app_id
    print easy.config.auto_fetch

.. rubric:: myconfig.yml

.. literalinclude:: ../../config.yaml
        :language: yaml
        :linenos:


Extending the Config
++++++++++++++++++++

Maybe you want to read your configuration from another source.
It is easy to archive, by extending the :py:class:`aboutyou.Config` class.

.. code-block:: python
    :linenos:

    from aboutyou import Config
    from pymongo import MongoClient

    class MongoDBClass(Config):

        def __init__(self, dburl='mongodb://localhost:27017/'):
            self.client = MongoClient(dburl)
            self.db = self.client['test-database']
            super(type(self), self).__init__()

        def __getattr__(self, name):
            return self.db.config.find_one().get(name)


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

