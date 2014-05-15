#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
from collins import Collins, Constants

import json


def testAutocomplete(collins, log):
    result = collins.autocomplete('sho', limit=10)
    log.info(json.dumps(result, indent=4))

    assert len(result) > 1


def testBasketset(collins, session, log):
    response = collins.basketset(session, [['my4813890', 4813890]])
    log.debug(json.dumps(response, indent=4))


def testBasketget(collins, session, log):
    response = collins.basketget(session)
    log.debug(json.dumps(response, indent=4))


def testBasketremove(collins, session, log):
    response = collins.basketremove(session, ['my4813890'])
    log.debug(json.dumps(response, indent=4))


def testCategory(collins, log):
    cat = collins.category([19586])
    log.info(cat)


def testCategorytree(collins):
    tree = collins.categorytree(max_depth=1)
    #self.log.info(tree)


def testFacets(collins, log):
    response = collins.facets([Constants.FACET_CUPSIZE])
    log.debug(json.dumps(response, indent=4))


def testFacettypes(collins, log):
    ftypes = collins.facettypes()
    log.info(set(ftypes)-Constants.FACETS)


def testOrder(collins):
    #collins.initiateorder(sessionid, sucess_url)
    pass


def testLivevariant(collins, log):
    response = collins.livevariant([4813890])
    log.debug(json.dumps(response, indent=4))


def testProducts(collins):
    #collins.products(ids)
    pass


def testProductsearch(collins, session):
    # i belive we search shorts now o.O
    response = collins.productsearch(session)

    assert len(response["products"]) > 0
    #self.log.info(response)


def testSuggest(collins):
    response = collins.suggest("ny")
    #self.log.info(response)
    assert len(response) > 0
