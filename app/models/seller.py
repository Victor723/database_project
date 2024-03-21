from flask import current_app as app


class Seller():
    def __init__(self, id, userkey, registrationdate):
        self.id = id
        self.userkey = userkey
        self.registrationdate = registrationdate

    @staticmethod
    def get_sellerkey(userkey):
        rows = app.db.execute("""
            SELECT s_sellerkey
            FROM Seller
            WHERE s_userkey = :userkey
            """,
            userkey=userkey)
        sellerkey = rows[0][0] if rows else None
        return sellerkey


    @staticmethod
    def get_product_info(sellerkey):
        rows = app.db.execute("""
            SELECT ps.ps_productkey, p.p_productname, ps.ps_quantity, ps.ps_price, ps.ps_discount, ps.ps_createtime
            FROM ProductSeller ps
            INNER JOIN Product p ON ps.ps_productkey = p.p_productkey
            WHERE ps.ps_sellerkey = :sellerkey
            """,
            sellerkey=sellerkey)
        
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
    def get_order_info(id):
        rows = app.db.execute("""
            SELECT l.l_orderkey, p.p_productname, o.o_ordercreatedate, 
                   CONCAT(u.u_firstname, ' ', u.u_lastname) AS customer_name, 
                   o.o_totalprice, CASE WHEN l.l_fulfillmentdate IS NULL THEN 'Pending' ELSE 'Fulfilled' END AS status
            FROM Lineitem l
            JOIN Orders o ON l.l_orderkey = o.o_orderkey
            JOIN Product p ON l.l_productkey = p.p_productkey
            JOIN Users u ON o.o_userkey = u.u_userkey
            WHERE l.l_sellerkey = :id
        """, id=id)
        
        order_info = []
        for row in rows:
            order_info.append({
                'order_id': row[0],
                'product_name': row[1],
                'date': row[2],
                'customer_name': row[3],
                'total_price': row[4],
                'status': row[5]
            })
            
        return order_info



    @staticmethod
    def get_seller_review(id):
        rows = app.db.execute("""
            SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_orderkey, sr_reviewdate, sr_review, sr_rating
            FROM SellerReview
            WHERE sr_sellerkey = :id
            """,
            id=id)
        return [row for row in rows]

