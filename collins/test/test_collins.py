#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon => [arne_simon@gmx.de]
"""
from collins.test import TEST_CONFIG, TEST_SESSION
import collins


class TestCollins:

    @staticmethod
    def setup_class(self):
        self.collins = collins.Collins(collins.JSONConfig(TEST_CONFIG))

    def setup_method(self, method):
        self.log = self.collins.log.getChild(method.__name__)

    def testAutocomplete(self):
        result = self.collins.autocomplete('sho', limit=10)
        #self.log.info(result)
        assert len(result) > 1

    def testBasketadd(self):
        #self.collins.basketadd(sessionid, products)
        pass

    def testBasketget(self):
        #self.collins.basketget(sessionid)
        pass

    def testCategory(self):
        cat = self.collins.category([16354])
        #self.log.info(cat)

    def testCategorytree(self):
        tree = self.collins.categorytree(max_depth=1)
        #self.log.info(tree)

    def testFacets(self):
        self.collins.facets([collins.Constants.FACET_CUPSIZE])

    def testFacettypes(self):
        ftypes = self.collins.facettypes()
        self.log.info(set(ftypes)-collins.Constants.FACETS)

    def testGetorder(self):
        #self.collins.getorder(orderid)
        pass

    def testInitiateorder(self):
        #self.collins.initiateorder(sessionid, sucess_url)
        pass

    def testLivevariant(self):
        #self.collins.livevariant(ids)
        pass

    def testProducts(self):
        #self.collins.products(ids)
        pass

    def testProductsearch(self):
        # i belive we search shorts now o.O
        response = self.collins.productsearch(TEST_SESSION,
                                              filter={"categories":[16354]})

        assert len(response["products"]) > 0
        #self.log.info(response)

    def testSuggest(self):
        response = self.collins.suggest("ny")
        #self.log.info(response)
        assert len(response) > 0
