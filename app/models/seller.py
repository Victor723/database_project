from flask import current_app as app


class Seller():
    def __init__(self, sellerkey, userkey, companyname, registrationdate):
        self.sellerkey = sellerkey
        self.userkey = userkey
        self.companyname = companyname
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
    def get_seller_information(sellerkey):
        rows = app.db.execute("""
            SELECT u.u_firstname, u.u_lastname, u.u_email, s.s_companyname, u.u_streetaddress, 
                   u.u_city, u.u_stateregion, u.u_zipcode, u.u_country, u.u_phonenumber
            FROM Seller s
            JOIN Users u ON s.s_userkey = u.u_userkey
            WHERE s.s_sellerkey = :sellerkey
            """, 
            sellerkey=sellerkey)

        seller_information = []
        for row in rows:
            seller_information.append({
                'first_name': row[0],
                'last_name': row[1],
                'email': row[2],
                'company_name': row[3],
                'street_address': row[4],
                'city': row[5],
                'state_region': row[6],
                'zipcode': row[7],
                'country': row[8],
                'phone_number': row[9],
            })
        return seller_information


    @staticmethod
    def get_order_info(sellerkey, limit=10, offset=0):
        rows = app.db.execute("""
            SELECT l.l_orderkey, p.p_productname, o.o_ordercreatedate, 
                CONCAT(u.u_firstname, ' ', u.u_lastname) AS customer_name, 
                o.o_totalprice, CASE WHEN l.l_fulfillmentdate IS NULL THEN 'Pending' ELSE 'Fulfilled' END AS status
            FROM Lineitem l
            JOIN Orders o ON l.l_orderkey = o.o_orderkey
            JOIN Product p ON l.l_productkey = p.p_productkey
            JOIN Users u ON o.o_userkey = u.u_userkey
            WHERE l.l_sellerkey = :sellerkey
            LIMIT :limit OFFSET :offset
        """, sellerkey=sellerkey, limit=limit, offset=offset)
        
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
    def get_total_order_count(sellerkey):
        row = app.db.execute("""
            SELECT COUNT(*)
            FROM Lineitem
            WHERE l_sellerkey = :sellerkey
        """, sellerkey=sellerkey)
        
        if row:
            # Extract count from the first row of the result list
            total_count = row[0][0] if row[0] else 0
            return total_count

        # Return 0 if there are no rows or if the first row is empty
        return 0


    @staticmethod
    def get_seller_review(sellerkey):
        rows = app.db.execute("""
            SELECT CONCAT(u.u_firstname, ' ', u.u_lastname) AS user_name, sr.sr_userkey, sr.sr_reviewdate, sr.sr_review, sr.sr_rating
            FROM SellerReview sr
            JOIN Users u ON sr.sr_userkey = u.u_userkey
            WHERE sr_sellerkey = :sellerkey
        """, sellerkey=sellerkey)

        seller_review = []
        for row in rows:
            seller_review.append({
                'user_name': row[0],
                'user_key': row[1],
                'date': row[2],
                'review': row[3],
                'rating': row[4]
            })
        return seller_review
