from flask import current_app as app

class Cart:
    def __init__(self, c_cartkey, c_userkey):
        self.c_cartkey = c_cartkey
        self.c_userkey = c_userkey

    @staticmethod
    def get(c_cartkey):
        rows = app.db.execute('''
        SELECT c_cartkey, c_userkey
        FROM Cart
        WHERE c_cartkey = :c_cartkey
        ''',
                              c_cartkey=c_cartkey)
        return Cart(*(rows[0])) if rows else None
    @staticmethod
    def get_products_keys_by_c_userkey(c_userkey):
        rows = app.db.execute('''
        SELECT pc.pc_productkey,
            pc.pc_sellerkey,
            pc.pc_savequantity,
            pc.pc_incartquantity
        FROM Cart c
        JOIN ProductCart pc ON c.c_cartkey = pc.pc_cartkey
        WHERE c.c_userkey = :c_userkey
        ''',
                                c_userkey=c_userkey)
        return rows if rows else None
    
    @staticmethod
    def get_incart_products_by_c_userkey(c_userkey):
        rows = app.db.execute('''
        SELECT p.p_productkey as product_key, -- Ensure this is correctly aliased for easy access
        p.p_productname,
        u.u_firstname,
        u.u_lastname,
        ps.ps_price,
        ps.ps_sellerkey as seller_key, -- Ensure seller key is also aliased
        pc.pc_incartquantity
        FROM Cart c
        JOIN ProductCart pc ON c.c_cartkey = pc.pc_cartkey
        JOIN ProductSeller ps ON pc.pc_productkey = ps.ps_productkey AND pc.pc_sellerkey = ps.ps_sellerkey
        JOIN Product p ON p.p_productkey = pc.pc_productkey
        JOIN Seller s ON s.s_sellerkey = ps.ps_sellerkey
        JOIN Users u ON s.s_userkey = u.u_userkey
        WHERE c.c_userkey = :c_userkey AND pc.pc_incartquantity > 0
        ''',
                                c_userkey=c_userkey)
        return rows if rows else None
    
    @staticmethod
    def get_save_products_by_c_userkey(c_userkey):
        rows = app.db.execute('''
        SELECT p.p_productname,
            u.u_firstname,
            u.u_lastname,
            ps.ps_price,
            pc.pc_savequantity AS savequantity
        FROM Cart c
        JOIN ProductCart pc ON c.c_cartkey = pc.pc_cartkey
        JOIN ProductSeller ps ON pc.pc_productkey = ps.ps_productkey AND pc.pc_sellerkey = ps.ps_sellerkey
        JOIN Product p ON p.p_productkey = pc.pc_productkey
        JOIN Seller s ON s.s_sellerkey = ps.ps_sellerkey
        JOIN Users u ON s.s_userkey = u.u_userkey
        WHERE c.c_userkey = :c_userkey
        ''',
                                c_userkey=c_userkey)
        return rows if rows else None
    
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
    def get_cartkey_by_user(c_userkey):
        result = app.db.execute('''
        SELECT c_cartkey
        FROM Cart c
        WHERE c.c_userkey = :c_userkey
        ''',
                                    c_userkey=c_userkey)
        return result[0][0] if result else None

    def add_to_cart(c_userkey, ps_productkey, ps_sellerkey, quantity):
        
        cartkey = Cart.get_cartkey_by_user(c_userkey)
        if not cartkey:
            print("No cart found for this user, creating new cart.")
            result = app.db.execute('''
            INSERT INTO Cart (c_userkey)
            VALUES (:c_userkey)
            RETURNING c_cartkey
            ''', c_userkey=c_userkey)
            cartkey = result[0][0]
            print(f"New cartkey: {cartkey}")
        
        if not ps_sellerkey:  # Check if sellerkey is empty
            print("Seller key is missing.")  # Note the indentation before print
            return None  # Return None to indicate failure


        # Check if the item already exists in the cart
        res = app.db.execute('''
        SELECT pc_incartquantity FROM ProductCart
        WHERE pc_cartkey = :cartkey AND pc_productkey = :productkey AND pc_sellerkey = :sellerkey
        ''', cartkey=cartkey, productkey=ps_productkey, sellerkey=ps_sellerkey)
        existing = res[0] if res else None
        if existing:
            # Update the existing quantity
            new_quantity = existing[0] + quantity
            result=app.db.execute('''
            UPDATE ProductCart SET pc_incartquantity = :new_quantity
            WHERE pc_cartkey = :cartkey AND pc_productkey = :productkey AND pc_sellerkey = :sellerkey
            ''', new_quantity=new_quantity, cartkey=cartkey, productkey=ps_productkey, sellerkey=ps_sellerkey)
        else:
            # Insert a new item into the cart
            result=app.db.execute('''
            INSERT INTO ProductCart (pc_cartkey, pc_productkey, pc_sellerkey, pc_savequantity, pc_incartquantity)
            VALUES (:cartkey, :productkey, :sellerkey, 0, :incartquantity)
            ''', cartkey=cartkey, productkey=ps_productkey, sellerkey=ps_sellerkey, incartquantity=quantity)
        return result

       
    @staticmethod
    def update_incart_quantity(c_userkey, product_key, seller_key, new_quantity):
        result = app.db.execute('''
        UPDATE ProductCart
        SET pc_incartquantity = :new_quantity
        WHERE pc_cartkey = (
            SELECT c_cartkey FROM Cart WHERE c_userkey = :c_userkey
        )
        AND pc_productkey = :product_key
        AND pc_sellerkey = :seller_key
        RETURNING pc_incartquantity
        ''',
        
            c_userkey =  c_userkey,
            product_key = product_key,
            seller_key = seller_key,
            new_quantity = new_quantity
        )
        if result and len(result) > 0 and len(result[0]) > 0:
            return result[0][0]  # Directly access the first element of the first tuple
        return None
    
    @staticmethod
    def update_save_quantity(c_userkey, product_key, seller_key, new_quantity):
        result = app.db.execute('''
        UPDATE ProductCart
        SET pc_savequantity = :new_quantity
        WHERE pc_cartkey = (
            SELECT c_cartkey FROM Cart WHERE c_userkey = :c_userkey
        )
        AND pc_productkey = :product_key
        AND pc_sellerkey = :seller_key
        RETURNING pc_savequantity
        ''',
        
            c_userkey =  c_userkey,
            product_key = product_key,
            seller_key = seller_key,
            new_quantity = new_quantity
        )
        if result and len(result) > 0 and len(result[0]) > 0:
            return result[0][0]  # Directly access the first element of the first tuple
        return None
    
    @staticmethod
    def remove_item(user_key, product_key, seller_key):
        
        num_rows_deleted = app.db.execute('''
            DELETE FROM ProductCart
            WHERE pc_productkey = :product_key
            AND pc_sellerkey = :seller_key
            AND pc_cartkey = (SELECT c_cartkey FROM Cart WHERE c_userkey = :user_key)
        ''', user_key=user_key, product_key=product_key, seller_key=seller_key)

        return num_rows_deleted > 0
    
    @staticmethod
    def move_to_save_for_later(c_userkey, product_key, seller_key):
        try:
            # Correcting the parameter names to match those in the SQL statement
            rows = app.db.execute('''
                UPDATE ProductCart
                SET pc_savequantity = pc_savequantity + pc_incartquantity,
                    pc_incartquantity = 0
                WHERE pc_cartkey = (SELECT c_cartkey FROM Cart WHERE c_userkey = :c_userkey)
                AND pc_productkey = :product_key
                AND pc_sellerkey = :seller_key
            ''', c_userkey=c_userkey,  # Corrected parameter name here
                product_key=product_key,
                seller_key=seller_key
            )
            return rows > 0
        except Exception as e:
            print(f"Error moving item to save for later: {e}")
            return False
        
    @staticmethod
    def delete_zero_quantity_items(cart_key):
        try:
            # Define the SQL query to delete entries where incartquantity is 0
            delete_query = '''
                DELETE FROM ProductCart
                WHERE pc_cartkey = :cart_key AND pc_incartquantity = 0;
            '''
            # Execute the delete operation
            rows_deleted = app.db.execute(delete_query, {'cart_key': cart_key})

            # You can log the number of rows deleted if needed
            print(f"Deleted {rows_deleted} items with zero quantity from cart {cart_key}.")

            return True
        except Exception as e:
            print(f"Error deleting zero quantity items from cart: {e}")
            return False

    @staticmethod
    def create_order_from_cart(user_key, cart_key):
        try:
            # Start by creating a new order and obtaining the order key
            insert_order_query = '''
                INSERT INTO Orders (o_userkey, o_totalprice, o_ordercreatedate)
                VALUES (:user_key, 0, CURRENT_DATE)
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
                    SET o_totalprice = (SELECT SUM(line_total) FROM MovedItems)
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