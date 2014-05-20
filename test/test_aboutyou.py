#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
from aboutyou import Constants

import json


def testAutocomplete(aboutyou, log):
    result = aboutyou.autocomplete('sho', limit=10)
    log.info(json.dumps(result, indent=4))

    assert len(result) > 1


def testBasketset(aboutyou, session, log):
    response = aboutyou.basket_set(session, [['my4813890', 4813890]])
    log.debug(json.dumps(response, indent=4))


def testBasketget(aboutyou, session, log):
    response = aboutyou.basket_get(session)
    log.debug(json.dumps(response, indent=4))


def testBasketremove(aboutyou, session, log):
    response = aboutyou.basket_remove(session, ['my4813890'])
    log.debug(json.dumps(response, indent=4))


def testCategory(aboutyou, log):
    cat = aboutyou.category([19586])
    log.info(cat)


def testCategorytree(aboutyou):
    tree = aboutyou.categorytree(max_depth=1)
    #self.log.info(tree)


def testFacets(aboutyou, log):
    response = aboutyou.facets([Constants.FACET_CUPSIZE])
    log.debug(json.dumps(response, indent=4))


def testFacettypes(aboutyou, log):
    ftypes = aboutyou.facettypes()
    log.info(set(ftypes)-Constants.FACETS)


def testOrder(aboutyou):
    #aboutyou.initiateorder(sessionid, sucess_url)
    pass


def testLivevariant(aboutyou, log):
    response = aboutyou.livevariant([4813890])
    log.debug(json.dumps(response, indent=4))


def testProducts(aboutyou):
    #aboutyou.products(ids)
    pass


def testProductsearch(aboutyou, session):
    # i belive we search shorts now o.O
    response = aboutyou.productsearch(session)

    assert len(response["products"]) > 0
    #self.log.info(response)


def testSuggest(aboutyou):
    response = aboutyou.suggest("ny")
    #self.log.info(response)
    assert len(response) > 0
