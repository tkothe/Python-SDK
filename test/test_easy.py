#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
from aboutyou.easy import EasyNode, SearchException


def test_categories(easy):
    tree = easy.categories()

    assert len(tree) > 0


def test_category_by_name(easy):
    c = easy.category_by_name("Damen")

    assert c is not None
    assert c.name == "Damen"


def test_category_by_id(easy):
    c = easy.category_by_id(19615)


def test_facet_groups(easy):
    groups = easy.facet_groups()


def test_facet_group_by_id(easy):
    group = easy.facet_group_by_id('color')


def test_products_by_id(easy):

    ids = [237188, 237116]
    try:
        products = easy.products_by_id(ids)
    except SearchException as e:
        products = e.found

    for p in products:
        assert p.id in ids

        assert p.categories is not None
        assert p.description_short is not None
        assert p.description_long is not None
        assert p.default_variant is not None
        assert p.default_image is not None
        assert p.variants is not None
        assert p.styles is not None


def test_products_by_ean(easy):
    products = easy.products_by_ean([370075138])


def test_search(easy, session):
    result = easy.search(session, filter={"categories":[19631, 19654]},
                         result={'fields': ['variants']})

    assert result.count > 0

    for p in result.products[:10]:
        for v in p.variants:
            assert v.id is not None


def test_simple_colors(easy):
    result = easy.simple_colors()

    assert len(result) > 0
    assert isinstance(result[0], EasyNode)


def test_basket(easy, session):
    try:
        basket = easy.basket(session)

        product = easy.products_by_id([434091])[0]

        variant = product.variants[0]

        print variant.live

        basket.set(variant, 1)

        costum = variant.costumize()

        # costum.additional_data['logo'] = 'Green Frog'

        basket.set(costum, 2)

        print basket.obj

        assert len(basket.obj['order_lines']) == 3

        assert basket.obj['order_lines'][0]['variant_id'] == variant.id

        print basket.buy('http://maumau.de')
    except Exception as e:
        raise e
    finally:
        basket.dispose()


def test_autocomplete(easy):
    easy.autocomplete('sho')


def test_suggest(easy):
    easy.suggest('sho')
