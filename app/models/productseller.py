from flask import current_app as app


class ProductSeller():
    def __init__(self, productkey, sellerkey, quantity, price, discount, createtime):
        self.productkey = productkey
        self.sellerkey = sellerkey
        self.quantity = quantity
        self.price = price
        self.discount = discount
        self.createtime = createtime
    

    @staticmethod
    def get_productseller_info(sellerkey, limit=10, offset=0):
        rows = app.db.execute("""
            SELECT ps.ps_productkey, p.p_productname, ps.ps_quantity, ps.ps_price, ps.ps_discount, ps.ps_createtime
            FROM ProductSeller ps
            INNER JOIN Product p ON ps.ps_productkey = p.p_productkey
            WHERE ps.ps_sellerkey = :sellerkey
            LIMIT :limit OFFSET :offset
            """,
            sellerkey=sellerkey, limit=limit, offset=offset)
        
        products = []
        for row in rows:
            product_info = {
                'productkey': row[0],
                'productname': row[1],
                'quantity': row[2],
                'price': row[3],
                'discount': row[4],
                'createtime': row[5]
            }
            products.append(product_info)      
        return products


    @staticmethod
    def get_total_product_count(sellerkey):
        row = app.db.execute("""
            SELECT COUNT(*)
            FROM ProductSeller
            WHERE ps_sellerkey = :sellerkey
            """,
            sellerkey=sellerkey)
        
        if row:
        # Extract count from the first row of the result list
            total_count = row[0][0] if row[0] else 0
            return total_count

        # Return 0 if there are no rows or if the first row is empty
        return 0


    @staticmethod
    def get_product_info(sellerkey, productkey):
        row = app.db.execute("""
            SELECT p.p_productkey, p.p_productname, p.p_price, p.p_description, p.p_imageurl, cat.cat_catkey, cat.cat_catname, ps.ps_quantity, ps.ps_discount, ps.ps_createtime
            FROM Product p
            INNER JOIN ProductSeller ps ON p.p_productkey = ps.ps_productkey
            INNER JOIN Category cat ON p.p_catkey = cat.cat_catkey
            WHERE ps.ps_sellerkey = :sellerkey AND p.p_productkey = :productkey
            """,
            sellerkey=sellerkey, productkey=productkey)

        if row[0]:
            # Construct a product information dictionary
            product_info = {
                'productkey': row[0][0],
                'productname': row[0][1],
                'price': row[0][2],
                'description': row[0][3],
                'imageurl': row[0][4],
                'category': f"({row[0][5]}) {row[0][6]}",
                'quantity': row[0][7],
                'discount': row[0][8],
                'createtime': row[0][9]
            }
            return product_info

        # Return None if no product information is found
        return None
