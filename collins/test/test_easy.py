#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon [arne.simon@slice-dice.de]
"""
from collins.test import TEST_CONFIG, TEST_SESSION
from collins import JSONConfig
from collins.easy import EasyCollins


class TestEasyCollins:

    @staticmethod
    def setup_class(self):
        config = JSONConfig(TEST_CONFIG)
        self.easy = EasyCollins(config)

    def testCategories(self):
        tree = self.easy.categories()

        assert len(tree) > 0

    def testCategoryByName(self):
        c = self.easy.categoryByName("Damen")

        assert c is not None
        assert c.name == "Damen"

    def testProductById(self):
        p = self.easy.productById(227838)

        assert p.id == 227838
        assert p.description_short is not None
        assert p.description_long is not None

    def testProductsById(self):
        ids = [237188, 237116]
        for p in self.easy.productsById(ids):
            assert p.id in ids

    def testSearch(self):
        result = self.easy.search(TEST_SESSION,
                                  filter={"categories":[19631, 19654]},
                                  result={})

        assert result.count > 0

        for p in result.products:
            for v in p.variants:
                # o.write(u"{}".format(v.obj))
                assert v.id is not None
