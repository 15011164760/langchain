
class shopList():
    def __init__(self,shopList):
        self.shopList = shopList
    def get_shop_count(self):
        return len(self.shopList)
    def get_total_price(self):
        total_price = 0
        for item in self.shopList:
            total_price += self.shopList[item]
        return total_price
