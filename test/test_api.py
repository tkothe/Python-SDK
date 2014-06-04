#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
from aboutyou.constants import FACET

import json


def test_autocomplete(aboutyou, log):
    result = aboutyou.autocomplete('sho', limit=10)


def test_suggest(aboutyou, log):
    result = aboutyou.suggest('sho')
    log.info(json.dumps(result, indent=4))


def test_basket_set(aboutyou, session, log):
    response = aboutyou.basket_set(session, [['my4813890', 4813890], ['my4813890-1', 4813890]])
    log.debug(json.dumps(response, indent=4))


def test_basket_get(aboutyou, session, log):
    response = aboutyou.basket_get(session)
    log.debug(json.dumps(response, indent=4))


def test_order(aboutyou, session):
    aboutyou.order(session, 'https://success.com')


def test_basket_remove(aboutyou, session, log):
    response = aboutyou.basket_remove(session, ['my4813890'])
    log.debug(json.dumps(response, indent=4))


def test_basket_dispose(aboutyou, session):
    aboutyou.basket_dispose(session)


def test_category(aboutyou, log):
    cat = aboutyou.category([19586])
    log.info(cat)


def test_categorytree(aboutyou):
    tree = aboutyou.categorytree(max_depth=1)


def test_facets(aboutyou, log):
    response = aboutyou.facets([FACET.CUPSIZE])
    log.debug(json.dumps(response, indent=4))


def test_facettypes(aboutyou, log):
    ftypes = aboutyou.facettypes()
    log.info(set(ftypes)-FACET.ALL)


def test_livevariant(aboutyou, log):
    response = aboutyou.livevariant([4813890])
    log.debug(json.dumps(response, indent=4))


def test_products(aboutyou):
    product = aboutyou.products([245372])['ids'][str(245372)]

    assert product['id'] == 245372


def test_producteans(aboutyou):
    product = aboutyou.producteans([370075138])


def test_productsearch(aboutyou, session):
    response = aboutyou.productsearch(session)

    assert len(response["products"]) > 0
    #self.log.info(response)
