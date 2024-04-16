from flask import current_app as app
class Order:
    def __init__(self, o_orderkey, o_userkey, o_totalprice, o_ordercreatedate):
        self.o_orderkey = o_orderkey
        self.o_userkey = o_userkey
        self.o_totalprice = o_totalprice
        self.o_ordercreatedate = o_ordercreatedate

    @staticmethod
    def get_orders(o_userkey, offset=0):
        query = '''
            SELECT 
                o.o_orderkey, 
                array_agg(p.p_productname) as product_names,
                o.o_totalprice as total_price, 
                o.o_ordercreatedate,
                COUNT(*) OVER() AS full_count
            FROM 
                Orders o
                JOIN Lineitem l ON o.o_orderkey = l.l_orderkey
                JOIN Product p ON l.l_productkey = p.p_productkey
            WHERE 
                o.o_userkey = :o_userkey
            GROUP BY 
                o.o_orderkey
            ORDER BY 
                o.o_ordercreatedate DESC
            LIMIT 
                10 OFFSET :offset;
        '''
        try:
            rows = app.db.execute(query, {'o_userkey': o_userkey, 'offset': offset}).fetchall()
            orders = [dict(row) for row in rows]
            return orders
        except Exception as e:
            app.logger.error(f"Error fetching orders: {e}")
            return []

    @staticmethod
    def get_orders(o_userkey, offset=0):
        query = '''
            SELECT 
                o.o_orderkey, 
                array_agg(p.p_productname) as product_names,
                o.o_totalprice as total_price, 
                o.o_ordercreatedate,
                COUNT(*) OVER() AS full_count
            FROM 
                Orders o
                JOIN Lineitem l ON o.o_orderkey = l.l_orderkey
                JOIN Product p ON l.l_productkey = p.p_productkey
            WHERE 
                o.o_userkey = :o_userkey
            GROUP BY 
                o.o_orderkey
            ORDER BY 
                o.o_ordercreatedate DESC
            LIMIT 
                10 OFFSET :offset;
        '''
        try:
            rows = app.db.execute(query, {'o_userkey': o_userkey, 'offset': offset}).fetchall()
            orders = [dict(row) for row in rows]
            return orders
        except Exception as e:
            app.logger.error(f"Error fetching orders: {e}")
            return []

    @staticmethod
    def check_product(userkey, productkey):
        query = '''
            SELECT EXISTS(
        SELECT 1
        FROM Orders o
        JOIN Lineitem l ON o.o_orderkey = l.l_orderkey
        WHERE o.o_userkey = :userkey AND l.l_productkey = :productkey
        );
        '''
        result = app.db.execute(query, {'userkey': userkey, 'productkey': productkey}).scalar()
        return result;

    @staticmethod
    def check_seller(userkey, sellerkey):
        query = '''
            SELECT EXISTS(
        SELECT 1
        FROM Orders o
        JOIN Lineitem l ON o.o_orderkey = l.l_orderkey
        WHERE o.o_userkey = :userkey AND l.l_sellerkey = :sellerkey
        );
        '''
        result = app.db.execute(query, {'userkey': userkey, 'sellerkey': sellerkey}).scalar()
        return result;
    