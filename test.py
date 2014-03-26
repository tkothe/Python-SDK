#-*- encoding: utf-8 -*-
"""
:Author:    Arne Simon => [arne_simon@gmx.de]
"""
import unittest
import collins


class ConfigTest(unittest.TestCase):
    def testNameResolution(self):
        conf = collins.Config("config.json")

        self.assertNotEqual(conf.app_id, None)

    def testImageName(self):
        name = "http://cdn.mary-paul.de/product_images/0/1_2_3.png"
        conf = collins.Config("config.json")

        self.assertEqual(conf.imageurl(0,1,2,3,".png"), name)


class CollinsTest(unittest.TestCase):

    def setUp(self):
        self.collins = collins.Collins(collins.Config("config.json"))

    def testAutocomplete(self):
        result = self.collins.autocomplete('sho')

    def testBasketadd(self):
        #self.collins.basketadd(sessionid, products)
        pass

    def testBasketget(self):
        pass

    def testCategory(self):
        pass

    def testCategorytree(self):
        pass

    def testFacets(self):
        pass

    def testFacettypes(self):
        pass

    def testGetorder(self):
        pass

    def testInitiateorder(self):
        pass

    def testLivevariant(self):
        pass

    def testProducts(self):
        pass

    def testProductsearch(self):
        pass

    def testSuggest(self):
        pass


if __name__ == '__main__':
    unittest.main()
