from flask import current_app as app
from datetime import datetime


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
    def get_product_info_sorted(id, sort_column, sort_order, limit=10, offset=0):
        # Ensure the sort column is valid to prevent SQL injection
        valid_columns = ['ps.ps_productkey', 'p.p_productname', 'ps.ps_quantity', 'ps.ps_price', 'ps.ps_discount', 'ps.ps_createtime']
        if sort_column not in valid_columns:
            sort_column = 'ps.ps_productkey'  # Default to sorting by product key if column is invalid

        # Ensure sort order is valid to prevent SQL injection
        valid_sort_orders = ['asc', 'desc']
        if sort_order not in valid_sort_orders:
            sort_order = 'asc'  # Default to ascending order if order is invalid

        # Build the SQL query dynamically with parameters
        query = """
            SELECT ps.ps_productkey, p.p_productname, ps.ps_quantity, ps.ps_price, ps.ps_discount, ps.ps_createtime
            FROM ProductSeller ps
            INNER JOIN Product p ON ps.ps_productkey = p.p_productkey
            WHERE ps.ps_sellerkey = :id
            ORDER BY {sort_column} {sort_order}
            LIMIT :limit OFFSET :offset
        """.format(sort_column=sort_column, sort_order=sort_order.upper())

        # Execute the query
        rows = app.db.execute(query, id=id, limit=limit, offset=offset)

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
    def get_total_product_count(id):
        row = app.db.execute("""
            SELECT COUNT(*)
            FROM ProductSeller
            WHERE ps_sellerkey = :id
            """,
            id=id)
        
        if row:
        # Extract count from the first row of the result list
            total_count = row[0][0] if row[0] else 0
            return total_count

        # Return 0 if there are no rows or if the first row is empty
        return 0


    @staticmethod
    def get_total_product_count(id):
        row = app.db.execute("""
            SELECT COUNT(*)
            FROM ProductSeller
            WHERE ps_sellerkey = :id
            """,
            id=id)
        
        if row:
        # Extract count from the first row of the result list
            total_count = row[0][0] if row[0] else 0
            return total_count

        # Return 0 if there are no rows or if the first row is empty
        return 0


    @staticmethod
    def search_products(sellerkey, search_query):
        # Query for products matching the search query
        rows = app.db.execute("""
            SELECT ps.ps_productkey, p.p_productname, ps.ps_quantity, ps.ps_price, ps.ps_discount, ps.ps_createtime
            FROM ProductSeller ps
            INNER JOIN Product p ON ps.ps_productkey = p.p_productkey
            WHERE ps.ps_sellerkey = :sellerkey
            AND (p.p_productname ILIKE :search_query OR ps.ps_productkey::TEXT ILIKE :search_query)
        """, sellerkey=sellerkey, search_query=f"%{search_query}%")

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
    def get_order_info(sellerkey, limit, offset):
        rows = app.db.execute("""
            SELECT l.l_orderkey, l_linenumber, p.p_productname, o.o_ordercreatedate, 
                CONCAT(u.u_firstname, ' ', u.u_lastname) AS customer_name, 
                l_originalprice, l_discount, l_tax, l_quantity,
                CASE WHEN l.l_fulfillmentdate IS NULL THEN 'Pending' ELSE 'Fulfilled' END AS status
            FROM Lineitem l
            JOIN Orders o ON l.l_orderkey = o.o_orderkey
            JOIN Product p ON l.l_productkey = p.p_productkey
            JOIN Users u ON o.o_userkey = u.u_userkey
            WHERE l.l_sellerkey = :sellerkey
            LIMIT :limit OFFSET :offset
        """, sellerkey=sellerkey, limit=limit, offset=offset)
        
        order_info = []
        for row in rows:
            origin_price = row[5]
            discount = row[6]
            tax = row[7]
            quantity = row[8]
            total_price = quantity * origin_price * (1 - discount) * (1 + tax)
            order_info.append({
                'order_id': row[0],
                "lineitem_id": row[1],
                'product_name': row[2],
                'date': row[3],
                'customer_name': row[4],
                'origin_price': origin_price,
                'discount': discount,
                'tax': tax,
                'quantity': quantity,
                'total_price': total_price,  # Calculate total price
                'status': row[9]
            })
            
        return order_info


    @staticmethod
    def get_lineitem_info(sellerkey, orderkey, lineitem_id):
        rows = app.db.execute("""
            SELECT l.l_orderkey, l_linenumber, p.p_productname, o.o_ordercreatedate, 
                CONCAT(u.u_firstname, ' ', u.u_lastname) AS customer_name, 
                l_originalprice, l_discount, l_tax, l_quantity,
                CASE WHEN l.l_fulfillmentdate IS NULL THEN 'Pending' ELSE 'Fulfilled' END AS status
            FROM Lineitem l
            JOIN Orders o ON l.l_orderkey = o.o_orderkey
            JOIN Product p ON l.l_productkey = p.p_productkey
            JOIN Users u ON o.o_userkey = u.u_userkey
            WHERE l.l_sellerkey = :sellerkey AND l.l_linenumber = :lineitem_id AND l.l_orderkey = :orderkey
        """, sellerkey=sellerkey, orderkey=orderkey, lineitem_id=lineitem_id)
        
        if rows:
            origin_price = rows[0][5]
            discount = rows[0][6]
            tax = rows[0][7]
            quantity = rows[0][8]
            total_price = quantity * origin_price * (1 - discount) * (1 + tax)
            lineitem_info = {
                'order_id': rows[0][0],
                "lineitem_id": rows[0][1],
                'product_name': rows[0][2],
                'date': rows[0][3],
                'customer_name': rows[0][4],
                'origin_price': origin_price,
                'discount': discount,
                'tax': tax,
                'quantity': quantity,
                'total_price': total_price,  
                'status': rows[0][9]
            }
        else:
            lineitem_info = None
            
        return lineitem_info


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


    @staticmethod
    def find_max_sellerkey():
        row = app.db.execute('''
            SELECT MAX(s_sellerkey)
            FROM Seller
        ''')
        return row[0][0] if row is not None else None


    @staticmethod
    def register(sellerkey, userkey, companyname, registrationdate):
        app.db.execute(
            """
            INSERT INTO Seller (s_sellerkey, s_userkey, s_companyname, s_registrationdate)
            VALUES (:sellerkey, :userkey, :companyname, :registrationdate)
            """,
            sellerkey=sellerkey,
            userkey=userkey,
            companyname=companyname,
            registrationdate=registrationdate
        )


    @staticmethod
    def order_finish(s_sellerkey, o_orderkey, l_linenumber):
        current_date = datetime.now()
        app.db.execute("""
            UPDATE Lineitem
            SET l_fulfillmentdate = :CURRENT_DATE
            WHERE l_sellerkey = :sellerkey AND l_orderkey = :orderkey AND l_linenumber = :linenumber
        """, CURRENT_DATE=current_date, sellerkey=s_sellerkey, orderkey=o_orderkey, linenumber=l_linenumber)
