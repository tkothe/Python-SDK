#-*- coding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
from aboutyou.api import AboutYouException
from aboutyou.constants import FACET
from aboutyou.easy import EasyNode, SearchException
from pytest import raises


def test_categories(easy):
    tree = easy.categories()

    assert len(tree) > 0

    categorie = tree[1]

    assert len(categorie.sub_categories) > 0


def test_category_by_name(easy):
    name = 'Subcategory 2.1'
    cat = easy.category_by_name(name)

    assert cat is not None
    assert cat.name == name


def test_category_by_id(easy):
    cat = easy.category_by_id(200)

    assert cat.id == 200
    assert cat.name == 'Main Category 2'


def test_facet_groups(easy):
    groups = easy.facet_groups()

    assert len(groups) > 0


def test_facet_group_by_id(easy):
    group = easy.facet_group_by_id('color')

    assert group.id == FACET.COLOR


def test_products_by_id(easy, mock):
    mock('products-full.json')

    ids = [123, 456]
    products = easy.products_by_id(ids)

    p = products[1]

    assert p.id in ids

    assert p.categories is not None
    assert p.description_short is not None
    assert p.description_long is not None
    assert p.default_variant is not None
    assert p.default_image is not None
    assert p.variants is not None
    assert p.styles is not None


# def test_products_by_ean(easy):
#     products = easy.products_by_ean([370075138])


# def test_search(easy, session):
#     result = easy.search(session, filter={"categories":[19631, 19654]},
#                          result={'fields': ['variants']})

#     assert result.count > 0

#     for p in result.products[:10]:
#         for v in p.variants:
#             assert v.id is not None


def test_simple_colors(easy):
    result = easy.simple_colors()

    assert len(result) > 0
    assert isinstance(result[0], EasyNode)


class TestBasket:
    def test_add(self, easy, session, mock):
        basket = easy.basket(session)

        mock('products-full.json')

        product = easy.products_by_id([123, 456])[1]

        variant = product.variants[0]

        mock('basket.json')

        basket.set(variant, 1)

    def test_remove(self, easy, session, mock):
        basket = easy.basket(session)

        pass

# def test_basket(easy, session):
#     try:
#         basket = easy.basket(session)

#         product = easy.products_by_id([434091])[0]

#         variant = product.variants[0]

#         print variant.live

#         basket.set(variant, 1)

#         costum = variant.costumize()

#         # costum.additional_data['logo'] = 'Green Frog'

#         basket.set(costum, 2)

#         print basket.obj

#         assert len(basket.obj['order_lines']) == 3

#         assert basket.obj['order_lines'][0]['variant_id'] == variant.id

#         print basket.buy('http://maumau.de')
#     except Exception as e:
#         raise e
#     finally:
#         basket.dispose()


def test_autocomplete(easy, mock):
    data = mock('autocomplete-sho.json')

    with raises(AboutYouException):
        products, categories = easy.autocomplete('sho')


def test_suggest(easy, mock):
    data = mock('suggest.json')
    easy.suggest('sho')
