from myshopList import shopList 
import unittest
class TestMyShopList(unittest.TestCase):
    def setUp(self):
        self.shopList = shopList({'apple': 2, 'banana': 3, 'orange': 1})
    def test_get_shop_count(self):
        self.assertEqual(self.shopList.get_shop_count(), 3)
    def test_get_total_price(self):
        self.assertEqual(self.shopList.get_total_price(), 6)