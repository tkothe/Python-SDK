#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon => [arne_simon@gmx.de]
"""
import unittest
import collins

TEST_CONFIG = "slicedice-config.json"
TEST_SESSION_ID = "fa8e2e2210n"


class ConfigTest(unittest.TestCase):
    def testNameResolution(self):
        conf = collins.Config(TEST_CONFIG)

        self.assertNotEqual(conf.app_id, None)

    def testImageName(self):
        name = "http://cdn.mary-paul.de/product_images/0/1_2_3.png"
        conf = collins.Config(TEST_CONFIG)

        self.assertEqual(conf.imageurl(0,1,2,3,".png"), name)


class CollinsTest(unittest.TestCase):

    @staticmethod
    def setUpClass():
        CollinsTest.collins = collins.Collins(TEST_CONFIG)

    def setUp(self):
        self.log = self.collins.log.getChild(self.id())

    def testAutocomplete(self):
        result = self.collins.autocomplete('sho', limit=10)
        self.log.info(result)
        self.assertGreater(len(result), 1)

    def testBasketadd(self):
        #self.collins.basketadd(sessionid, products)
        pass

    def testBasketget(self):
        #self.collins.basketget(sessionid)
        pass

    def testCategory(self):
        self.log.info(self.collins.category([16354]))

    def testCategorytree(self):
        self.log.info(self.collins.categorytree(max_depth=1))

    def testFacets(self):
        self.log.info(self.collins.facets([collins.Constants.FACET_COLOR]))

    def testFacettypes(self):
        ftypes = self.collins.facettypes()
        self.log.info(set(ftypes)-collins.Constants.FACETS)
        self.log.info(self.collins.facettypes())

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
        response = self.collins.productsearch(TEST_SESSION_ID, filter={"categories":[16354]}) # i belive we search shorts now o.O
        self.log.info(response)

    def testSuggest(self):
        response = self.collins.suggest("ny")
        self.log.info(response)
        self.assertGreater(len(response), 0)


if __name__ == '__main__':
    unittest.main()
