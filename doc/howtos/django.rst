How To use with Django
======================

Some examples how to use the SDK with Django.

Setup
-----

It is a good practice to put an instance of :py:class:`aboutyou.Aboutyou` or
:py:class:`aboutyou.easy.EasyAboutYou` in the *settings.py* of django, so
the entire application can access one instance.

**settings.py**

.. code-block:: python

    ABOUTYOU = None

    try:
        from aboutyou import YAMLConfig
        from aboutyou.easy import EasyAboutYou

        aboutyou_config = YAMLConfig('slicedice-config.yml')
        ABOUTYOU = EasyAboutYou(aboutyou_config)
    except:
        logger.exception('No AboutYou API!!!')


Search Template Tag
-------------------

.. code-block:: python

    from django import template
    from django.conf import settings

    from aboutyou import Constants

    import logging

    register = template.Library()
    logger = logging.getLogger("aboutyou.templatetags")

    def buildproduct(p):
        return {
            "id": p.id,
            "vid": p.default_variant.id,
            "name": p.name,
            "url": p.default_variant.images[0].url(150, 150),
            "price": '{:.2f}'.format(float(p.default_variant.price)/100.0).replace('.', ','),
            "brands": ', '.join([f.name for f in p.default_variant.attributes['brand'] if not f.name.startswith('unknown')]),
        }

    @register.filter(name='search')
    def search(product, session):
        try:
            if session.session_key is None:
                session.cycle_key()

            if isinstance(product, Product):
                filters = {
                            "categories": [product.category],
                            "facets": {Constants.FACET_COLOR: [product.color]},
                        }

                result = {
                    "fields": ["variants", "active", "description_short",
                                "description_long", "default_variant"]
                }

                search = settings.ABOUTYOU.search(session.session_key, filters, result)

                prods = search.products[:20]

                return [buildproduct(p) for p in prods]
            else:
                logger.error("passing none product {} to search".format(product))
        except:
            logger.exception('')

        return None


.. code-block:: html

    {% with product|search:request.session as result %}
    {% if result|length > 0 %}
        <h2 class="productHeading">
            <div class="marker">{{ forloop.counter }}</div>
            Produktvorschl&auml;ge
        </h2>

        {% for p in result %}
        <a class="" href="#" title="{{ p.name }}" target="_blank" data-id="{{ p.id }}" data-variant="{{ p.vid }}">
            <div class="product">
                <img class="productImg" src="{{ p.url }}" alt="{{ p.name }}" />
            </div>
            <p class="title truncate">{{ p.name }}</p>
            {% if p.brands != '' %}<p class="brand">{{ p.brands }}</p>{% endif %}
            <p class="price">{{ p.price }} &euro;</p>
        </a>
        {% endfor %}
    {% endif %}
