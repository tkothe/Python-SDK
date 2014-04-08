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

    def testSearch(self):
        result = self.easy.search(TEST_SESSION,
                                  {"sale": True},
                                  {"sale":True, "limit": 2})

        assert result.count > 0
