#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
from collins.easy import EasyNode


def testCategories(easy):
    tree = easy.categories()

    assert len(tree) > 0


def testCategoryByName(easy):
    c = easy.categoryByName("Damen")

    assert c is not None
    assert c.name == "Damen"


def testProductById(easy):
    products = easy.productsById([227838])

    assert len(products) == 1

    p = products[0]

    assert p.id == 227838
    assert p.description_short is not None
    assert p.description_long is not None


def testProductsById(easy):
    ids = [237188, 237116]
    for p in easy.productsById(ids):
        assert p.id in ids


def testSearch(easy, session):
    result = easy.search(session, filter={"categories":[19631, 19654]},
                         result={'fields': ['variants']})

    assert result.count > 0

    for p in result.products:
        for v in p.variants:
            assert v.id is not None


def testSimpleColors(easy):
    result = easy.getSimpleColors()

    assert len(result) > 0
    assert isinstance(result[0], EasyNode)
