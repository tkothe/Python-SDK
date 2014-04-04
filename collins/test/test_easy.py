#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon => [arne_simon@gmx.de]
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

    def testProductById(self):
        p = self.easy.productById(227838)

        assert p.id == 227838

    def testSearch(self):
        search = self.easy.search(TEST_SESSION)

        search.filter.sale = True
        search.result.sale = True
        search.result.limit = 2

        result = search.perform()
