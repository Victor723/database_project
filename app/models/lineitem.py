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
        # SQL to check for any NULL fulfillment dates for the order
        check_query = '''
            SELECT COUNT(*) FROM Lineitem
            WHERE l_orderkey = :l_orderkey AND l_fulfillmentdate IS NULL;
        '''
        count_result = app.db.execute(check_query, l_orderkey = l_orderkey)
        unfulfilled_count = count_result[0][0]

        # If there is any unfulfilled line item, return False
        if unfulfilled_count > 0:
            return False

        # Since all items are fulfilled, get the latest fulfillment date
        date_query = '''
            SELECT MAX(l_fulfillmentdate) FROM Lineitem
            WHERE l_orderkey = :l_orderkey;
        '''
        date_result = app.db.execute(date_query, l_orderkey = l_orderkey)
        newest_fulfillmentdate = date_result[0][0]

        # Return the newest fulfillment date or False if it doesn't exist
        return newest_fulfillmentdate if newest_fulfillmentdate else False
    
    @staticmethod
    def check_product(user_key, product_key):
        query = '''
            SELECT EXISTS(
                SELECT 1
                FROM Orders o
                JOIN Lineitem l ON o.o_orderkey = l.l_orderkey
                WHERE o.o_userkey = :userkey AND l.l_productkey = :productkey
            );
        '''
        results = app.db.execute(query, l_orderkey=l_orderkey)
    
    @staticmethod
    def check_product(user_key, product_key):
        query = '''
            SELECT EXISTS(
                SELECT 1
                FROM Orders o
                JOIN Lineitem l ON o.o_orderkey = l.l_orderkey
                WHERE o.o_userkey = :userkey AND l.l_productkey = :productkey
            );
        '''
        result = app.db.execute(query, userkey=user_key, productkey=product_key)
        return result[0][0] if result else False

    @staticmethod
    def check_seller(user_key, seller_key):
        query = '''
            SELECT EXISTS(
                SELECT 1
                FROM Orders o
                JOIN Lineitem l ON o.o_orderkey = l.l_orderkey
                WHERE o.o_userkey = :userkey AND l.l_sellerkey = :sellerkey
            );
        '''
        result = app.db.execute(query, userkey=user_key, sellerkey=seller_key)
        return result[0][0] if result else False