from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy

class Cart():
    def __init__(self, c_cartkey, c_userkey):
        self.c_cartkey = c_cartkey
        self.c_userkey = c_userkey
    
    @staticmethod
    def get_incart_products_by_userkey(c_userkey):
        result = app.db.execute('''
        SELECT
            p.p_productkey as product_key,
            p.p_productname,
            u.u_firstname,
            u.u_lastname,
            ps.ps_price,
            ps.ps_sellerkey as seller_key,
            pc.pc_incartquantity,
            ROUND((ps.ps_price * pc.pc_incartquantity)::numeric, 2) AS subtotal
        FROM Cart c
        JOIN ProductCart pc ON c.c_cartkey = pc.pc_cartkey
        JOIN ProductSeller ps ON pc.pc_productkey = ps.ps_productkey AND pc.pc_sellerkey = ps.ps_sellerkey
        JOIN Product p ON p.p_productkey = pc.pc_productkey
        JOIN Seller s ON s.s_sellerkey = ps.ps_sellerkey
        JOIN Users u ON s.s_userkey = u.u_userkey
        WHERE c.c_userkey = :c_userkey AND pc.pc_incartquantity > 0

        ''',
                                c_userkey=c_userkey)
        
        keys = ['product_key', 'p_productname', 'u_firstname', 'u_lastname', 'ps_price', 'seller_key', 'pc_incartquantity', 'subtotal']
        
        # Create dictionaries from each tuple in the result
        cart_items = [dict(zip(keys, row)) for row in result]
        
        return cart_items
    
    @staticmethod
    def get_save_products_by_c_userkey(c_userkey):
        rows = app.db.execute('''
        SELECT 
            p.p_productkey as product_key,        
            p.p_productname,
            u.u_firstname,
            u.u_lastname,
            ps.ps_price,
            ps.ps_sellerkey as seller_key,
            pc.pc_savequantity AS savequantity
        FROM Cart c
        JOIN ProductCart pc ON c.c_cartkey = pc.pc_cartkey
        JOIN ProductSeller ps ON pc.pc_productkey = ps.ps_productkey AND pc.pc_sellerkey = ps.ps_sellerkey
        JOIN Product p ON p.p_productkey = pc.pc_productkey
        JOIN Seller s ON s.s_sellerkey = ps.ps_sellerkey
        JOIN Users u ON s.s_userkey = u.u_userkey
        WHERE c.c_userkey = :c_userkey AND pc_savequantity > 0
        ''',
                                c_userkey=c_userkey)
        
        keys = ['product_key', 'p_productname', 'u_firstname', 'u_lastname', 'ps_price', 'seller_key', 'pc_savequantity']
        save_items = [dict(zip(keys, row)) for row in rows]
        return save_items
    
    @staticmethod
    def get_incart_total_cost_by_c_userkey(c_userkey):
        query = '''
        SELECT SUM(ps.ps_price * pc.pc_incartquantity) AS total_cost
        FROM Cart c
        JOIN ProductCart pc ON c.c_cartkey = pc.pc_cartkey
        JOIN ProductSeller ps ON pc.pc_productkey = ps.ps_productkey AND pc.pc_sellerkey = ps.ps_sellerkey
        WHERE c.c_userkey = :c_userkey
        GROUP BY c.c_userkey
        '''
        result_list = app.db.execute(query, c_userkey=c_userkey)
        # Since result is a list, we take the first element (which is the tuple) and then take the first item from it.
        total_cost = round(result_list[0][0], 2) if result_list else 0.00
        # Return the total cost.
        return total_cost

    @staticmethod
    def get_or_create_cartkey_by_user(c_userkey):
        result = app.db.execute('''
        SELECT c_cartkey
        FROM Cart c
        WHERE c.c_userkey = :c_userkey
        ''',
                                    c_userkey=c_userkey)
        cartkey = result[0][0] if result else None
        if not cartkey:
            result = app.db.execute('''
                INSERT INTO Cart (c_userkey)
                VALUES (:c_userkey)
                RETURNING c_cartkey
                ''', c_userkey=c_userkey)
            cartkey = result[0][0]
        return cartkey

    @staticmethod
    def create_order_from_cart(user_key, cart_key):
        try:
            # Start by creating a new order and obtaining the order key
            insert_order_query = '''
                INSERT INTO Orders (o_userkey, o_totalprice, o_ordercreatedate)
                VALUES (:user_key, 0, CURRENT_TIMESTAMP)
                RETURNING o_orderkey;
            '''
            # Execute the query and retrieve the new order key directly
            order_key = app.db.execute(insert_order_query, user_key=user_key)[0][0]

            # Insert items into Lineitem and calculate total price in one step
            update_cart_and_create_lineitems = '''
                WITH MovedItems AS (
                    INSERT INTO Lineitem (l_orderkey, l_linenumber, l_productkey, l_sellerkey, l_quantity, l_originalprice, l_tax)
                    SELECT 
                        :order_key,
                        COALESCE((SELECT MAX(l_linenumber) FROM Lineitem WHERE l_orderkey = :order_key), 0) + row_number() OVER (ORDER BY pc_productkey, pc_sellerkey),
                        pc_productkey, 
                        pc_sellerkey, 
                        pc_incartquantity, 
                        ps_price, 
                        0.0
                    FROM ProductCart
                    JOIN ProductSeller ON ProductCart.pc_productkey = ProductSeller.ps_productkey AND ProductCart.pc_sellerkey = ProductSeller.ps_sellerkey
                    WHERE pc_cartkey = :cart_key AND pc_incartquantity > 0
                    RETURNING l_originalprice * l_quantity AS line_total
                ),
                UpdatedOrder AS (
                    UPDATE Orders
                    SET o_totalprice = COALESCE((SELECT SUM(line_total) FROM MovedItems), 0)
                    WHERE o_orderkey = :order_key
                )
                UPDATE ProductCart
                SET pc_incartquantity = 0
                WHERE pc_cartkey = :cart_key;
            '''
            # Execute the update and line item creation as a single operation
            app.db.execute(update_cart_and_create_lineitems, order_key=order_key, cart_key=cart_key)

            return True
        except Exception as e:
            print(f"Error creating order from cart: {e}")
            return False
