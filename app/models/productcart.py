from flask import current_app as app
from app.models.cart import Cart
from app.models.productseller import ProductSeller


class ProductCart():
    # __tablename__ = 'ProductCart'
    # pc_prodcartkey = db.Column(db.BigInteger, primary_key=True)
    # pc_cartkey = db.Column(db.BigInteger, db.ForeignKey('Cart.c_cartkey'), nullable=False)
    # pc_productkey = db.Column(db.BigInteger, nullable=False)
    # pc_sellerkey = db.Column(db.BigInteger, nullable=False)
    # pc_savequantity = db.Column(db.BigInteger, nullable=False, default=0)
    # pc_incartquantity = db.Column(db.BigInteger, nullable=False, default=0)

    # cart = db.relationship('Cart', back_populates='product_carts')
    # product_seller = db.relationship('ProductSeller', back_populates='product_carts')

    def __init__(self, pc_cartkey, pc_productkey, pc_sellerkey, pc_savequantity, pc_incartquantity):
        self.pc_cartkey = pc_cartkey
        self.pc_productkey = pc_productkey
        self.pc_sellerkey = pc_sellerkey
        self.pc_savequantity = pc_savequantity
        self.pc_incartquantity = pc_incartquantity

    @staticmethod
    def get_incart_quantity(cart_key, product_key, seller_key):
        """Get incart quantity for a specific product in the cart """
        sql = '''
            SELECT pc_incartquantity
            FROM ProductCart
            WHERE pc_cartkey = :cart_key AND pc_productkey = :product_key AND pc_sellerkey = :seller_key
        '''
        result = app.db.execute(sql, 
            cart_key=cart_key,
            product_key=product_key,
            seller_key=seller_key)
        if result and len(result) > 0 and len(result[0]) > 0:
            return result[0][0]  # Directly access the first element of the first tuple
        return None

    @staticmethod
    def get_save_quantity(cart_key, product_key, seller_key):
        """Get save quantity for a specific product in the cart """
        sql = '''
            SELECT pc_savequantity
            FROM ProductCart
            WHERE pc_cartkey = :cart_key AND pc_productkey = :product_key AND pc_sellerkey = :seller_key
        '''
        result = app.db.execute(sql, 
            cart_key=cart_key,
            product_key=product_key,
            seller_key=seller_key
       )
        if result and len(result) > 0 and len(result[0]) > 0:
            return result[0][0]  # Directly access the first element of the first tuple
        return None
    
    @staticmethod
    def update_incart_quantity(cart_key, product_key, seller_key, new_quantity):
        """Update incart quantity for a specific product in the cart """
        sql = '''
            UPDATE ProductCart
            SET pc_incartquantity = :new_quantity
            WHERE pc_cartkey = :cart_key AND pc_productkey = :product_key AND pc_sellerkey = :seller_key
            RETURNING pc_incartquantity
        '''
        result = app.db.execute(sql, 
            new_quantity=new_quantity,
            cart_key=cart_key,
            product_key=product_key,
            seller_key=seller_key)
        if result and len(result) > 0 and len(result[0]) > 0:
            return result[0][0]  # Directly access the first element of the first tuple
        return None

    @staticmethod
    def update_save_quantity(cart_key, product_key, seller_key, new_quantity):
        """Update save quantity for a specific product in the cart """
        sql = '''
            UPDATE ProductCart
            SET pc_savequantity = :new_quantity
            WHERE pc_cartkey = :cart_key AND pc_productkey = :product_key AND pc_sellerkey = :seller_key
        RETURNING pc_savequantity
        '''
        result = app.db.execute(sql, 
            new_quantity=new_quantity,
            cart_key=cart_key,
            product_key=product_key,
            seller_key=seller_key
       )
        if result and len(result) > 0 and len(result[0]) > 0:
            return result[0][0]  # Directly access the first element of the first tuple
        return None

    @staticmethod
    def remove_item(cart_key, product_key, seller_key):
        """Remove a specific product from the cart """
        sql = '''
            DELETE FROM ProductCart
            WHERE pc_cartkey = :cart_key AND pc_productkey = :product_key AND pc_sellerkey = :seller_key
        '''
        result = app.db.execute(sql, 
            cart_key=cart_key,
            product_key=product_key,
            seller_key=seller_key
       )
        return result > 0

    @staticmethod
    def move_to_save_for_later(cart_key, product_key, seller_key):
        """Move a product from in-cart to save-for-later """
        sql = '''
            UPDATE ProductCart
            SET pc_savequantity = pc_savequantity + pc_incartquantity,
                pc_incartquantity = 0
            WHERE pc_cartkey = :cart_key AND pc_productkey = :product_key AND pc_sellerkey = :seller_key
        '''
        result = app.db.execute(sql, 
            cart_key=cart_key,
            product_key=product_key,
            seller_key=seller_key
       )
        return result > 0

    @staticmethod
    def move_to_incart(cart_key, product_key, seller_key):
        """Move a product from save-for-later to in-cart """
        sql = '''
            UPDATE ProductCart
            SET pc_incartquantity = pc_incartquantity + pc_savequantity,
                pc_savequantity = 0
            WHERE pc_cartkey = :cart_key AND pc_productkey = :product_key AND pc_sellerkey = :seller_key
        '''
        result = app.db.execute(sql, 
            cart_key=cart_key,
            product_key=product_key,
            seller_key=seller_key
       )
        return result > 0

    @staticmethod
    def delete_zero_quantity_items(cart_key):
        """Delete ProductCart entries where both in-cart and save quantities are zero """
        sql = '''
            DELETE FROM ProductCart
            WHERE pc_cartkey = :cart_key AND pc_incartquantity = 0 AND pc_savequantity = 0
        '''
        result = app.db.execute(sql, cart_key=cart_key)
        return result > 0
    
    @staticmethod
    def check_and_get_existing_product(cart_key, product_key, seller_key):
        """ Check if the product already exists in the cart and return the current quantity. """
        result = app.db.execute('''
            SELECT pc_incartquantity FROM ProductCart
            WHERE pc_cartkey = :cartkey AND pc_productkey = :product_key AND pc_sellerkey = :seller_key
        ''', cartkey=cart_key, product_key= product_key, seller_key=seller_key)
        return result[0] if result else None

    @staticmethod
    def insert_new_product(cart_key, product_key, seller_key, quantity):
        """ Insert a new product into the cart. """
        app.db.execute('''
            INSERT INTO ProductCart (pc_cartkey, pc_productkey, pc_sellerkey, pc_savequantity, pc_incartquantity)
            VALUES (:cartkey, :product_key, :seller_key, 0, :incartquantity)
        ''', cartkey=cart_key, product_key=product_key, seller_key=seller_key, incartquantity=quantity)

    @staticmethod
    def add_to_cart(c_userkey, ps_productkey, ps_sellerkey, quantity):
        """ Manage the process of adding items to the cart, checking inventory, and updating or inserting cart items. """
        inventory_status = ProductSeller.check_inventory_and_return_status(ps_productkey, ps_sellerkey, quantity)
        
        if not inventory_status['available']:
            return {"success": False, "message": inventory_status['message']}

        cart_key = Cart.get_or_create_cartkey_by_user(c_userkey)
        existing_product = ProductCart.check_and_get_existing_product(cart_key, ps_productkey, ps_sellerkey)
        
        if existing_product:
            new_quantity = existing_product[0] + (inventory_status.get('quantity', quantity))
            ProductCart.update_incart_quantity(cart_key, ps_productkey, ps_sellerkey, new_quantity)
        else:
            ProductCart.insert_new_product(cart_key, ps_productkey, ps_sellerkey, inventory_status.get('quantity', quantity))
        
        return {"success": True, "message": inventory_status['message']}
