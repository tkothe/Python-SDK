#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon => [arne_simon@gmx.de]
"""
import unittest
import collins

TEST_CONFIG = "../python-shop-config.json"


class ConfigTest(unittest.TestCase):
    def testNameResolution(self):
        conf = collins.Config(TEST_CONFIG)

        self.assertNotEqual(conf.app_id, None)

    def testImageName(self):
        name = "http://cdn.mary-paul.de/product_images/0/1_2_3.png"
        conf = collins.Config(TEST_CONFIG)

        self.assertEqual(conf.imageurl(0,1,2,3,".png"), name)


class CollinsTest(unittest.TestCase):

    def setUp(self):
        self.collins = collins.Collins(collins.Config(TEST_CONFIG))

    def testAutocomplete(self):
        result = self.collins.autocomplete('sho')

        self.assertGreater(len(result), 1)

    def testBasketadd(self):
        #self.collins.basketadd(sessionid, products)
        pass

    def testBasketget(self):
        #self.collins.basketget(sessionid)
        pass

    def testCategory(self):
        #self.collins.category(ids)
        pass

    def testCategorytree(self):
        self.collins.categorytree()

    def testFacets(self):
        self.collins.facets()

    def testFacettypes(self):
        self.collins.facettypes()

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
        #self.collins.productsearch(sessionid)
        pass

    def testSuggest(self):
        response = self.collins.suggest("ny")
        self.collins.log.info(response)

        self.assertGreater(len(response), 0)


if __name__ == '__main__':
    unittest.main()
