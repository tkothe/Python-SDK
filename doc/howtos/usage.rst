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
Then use the :py:class:`aboutyou.config.Credentials` class direktly.

.. code-block:: python
    :linenos:

    from aboutyou.config import Credentials
    from aboutyou.api import Aboutyou

    credentials = Credentials(app_id=101, app_token="<yourtoken>")
    client = Aboutyou(credentials)

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

    from aboutyou.config import YAMLConfig, YAMLCredentials
    from aboutyou.api import Aboutyou

    client = Aboutyou(YAMLCredentials('mycredentials.yml'), YAMLConfig('myconfig.yml'))

    print client.credentials.app_id
    print client.config.auto_fetch

.. rubric:: mycredentials.yml

.. literalinclude:: ../../examples/credentials.yml
    :language: yaml
    :linenos:

.. rubric:: myconfig.yml

.. literalinclude:: ../../examples/config.yaml
    :language: yaml
    :linenos:


Extending the Config
++++++++++++++++++++

Maybe you want to read your configuration from another source.
It is easy to archive, by extending the :py:class:`aboutyou.Config` class.

.. code-block:: python
    :linenos:

    from aboutyou.config import Config
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

    p = easy.products_by_id([239982])[0]

    print p.name

    for v in p.variants:
        print v.id
        print [f.name for f in v.attributes["brand"]]


Many products by id
--------------------

If you want to get products directly by its id.

.. code-block:: python
    :linenos:

    from aboutyou.config import YAMLCredentials
    from aboutyou.shop import ShopApi, SearchException

    client = ShopApi(YAMLCredentials("mycredentials.yml"))

    try:
        for p in easy.products_by_id([237188, 237116]):
            print p.name
    except SearchException as e:
        print e.withError   # list of tuples (id, [errors]) for not found products
        print e.found       # list of found products


Category Tree
-------------

.. code-block:: python
    :linenos:

    from aboutyou.shop import ShopApi
    from aboutyou.config import JSONConfig

    easy = ShopApi(JSONConfig('myconfig.json'))

    # all categories of the first level
    for c in easy.categories():
        print '---', c.name, '---'
        for sub in c:
            print sub.name

    damen = easy.categoryByName("Damen")

    print damen.id, damen.name


Using the Basket
----------------

.. code-block:: python
    :linenos:

    from aboutyou.config import YAMLConfig
    from aboutyou.shop import ShopApi

    easy = ShopApi(YAMLConfig('myconf.yml'))

    basket = easy.basket(session)

    product = easy.productsById([434091])[0]

    variant = product.variants[0]

    print variant.live

    # we want one normal variant from our product
    basket.set(variant, 1)

    # lets costumize the variant
    costum = variant.costumize()

    costum.additional_data['description'] = 'Green Frog Logo'

    # add two costumized varaints to the basket
    basket.set(costum, 2)

    # lets costumize the variant, again
    costum2 = variant.costumize()

    costum2.additional_data['description'] = 'Funky Frog Logo'

    # add five costumized varaints to the basket
    basket.set(costum2, 5)

    print basket.total_net, basket.total_vat, basket.total_price

    checkout_url = basket.buy('https://success.com')

