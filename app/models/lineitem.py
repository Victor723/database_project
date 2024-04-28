from flask import current_app as app

class Lineitem:
    def __init__(self, l_linenumber, l_orderkey, l_productkey, l_sellerkey, l_quantity, l_originalprice, l_fulfillmentdate, l_discount, l_tax):
        self.l_linenumber = l_linenumber
        self.l_orderkey = l_orderkey
        self.l_productkey = l_productkey
        self.l_sellerkey = l_sellerkey
        self.l_quantity = l_quantity
        self.l_originalprice = l_originalprice
        self.l_fulfillmentdate = l_fulfillmentdate
        self.l_discount = l_discount
        self.l_tax = l_tax


    @staticmethod
    def is_fulfilled(l_orderkey):
        query = '''
        SELECT l_fulfillmentdate IS NOT NULL AS fulfilled
        FROM Lineitem
        WHERE l_orderkey = :l_orderkey;
        '''
        results = app.db.execute(query, l_orderkey=l_orderkey)
        return all(result[0] for result in results) if results else False
