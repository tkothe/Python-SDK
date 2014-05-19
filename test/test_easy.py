#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
from aboutyou.easy import EasyNode


def testCategories(easy):
    tree = easy.categories()

    assert len(tree) > 0


def testCategoryByName(easy):
    c = easy.categoryByName("Damen")

    assert c is not None
    assert c.name == "Damen"


def testProductsById(easy):
    # Boar, testing with fix product ids is BAD, because they change so rapidly!

    # ids = [237188, 237116]
    # products = easy.productsById(ids)

    # assert len(products) == 2

    # assert products[0].id == 227838
    # assert products[0].id == 237116

    # for p in products:
    #     assert p.id in ids

    #     assert p.description_short is not None
    #     assert p.description_long is not None
    pass

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
