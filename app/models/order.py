from flask import current_app as app
from app.models.productseller import ProductSeller    
class Order:
    def __init__(self, o_orderkey, o_userkey, o_totalprice, o_ordercreatedate):
        self.o_orderkey = o_orderkey
        self.o_userkey = o_userkey
        self.o_totalprice = o_totalprice
        self.o_ordercreatedate = o_ordercreatedate

    @staticmethod
    def get_orders(o_userkey, offset=0, per_page=10, start_date=None, end_date=None):
        date_filter = ""
        params = {'o_userkey': o_userkey, 'offset': offset, 'per_page': per_page}
        if start_date:
            date_filter += " AND o.o_ordercreatedate >= :start_date"
            params['start_date'] = start_date.strftime('%Y-%m-%d')
        if end_date:
            date_filter += " AND o.o_ordercreatedate <= :end_date"
            params['end_date'] = end_date.strftime('%Y-%m-%d')

        query = f'''
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
                {date_filter}
            GROUP BY 
                o.o_orderkey
            ORDER BY 
                o.o_ordercreatedate DESC
            LIMIT 
                :per_page OFFSET :offset;
        '''
        rows = app.db.execute(query, **params)
        orders = []
        total_orders = 0
        for row in rows:
            if not total_orders:
                total_orders = row[4]  # Assuming the count is the same for all rows
            order = {
                'o_orderkey': row[0],
                'product_names': ', '.join(row[1]),
                'total_price': row[2],
                'o_ordercreatedate': row[3].strftime('%Y-%m-%d'),
            }
            orders.append(order)
        # Note: total_orders is the count from the first row, which should be the same for all rows
        return orders, total_orders


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
        return result

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

    @staticmethod
    def get_order_details(order_id):
        order_details = {}
        
        # Fetch the basic order details
        order_query = "SELECT o_orderkey, o_totalprice, o_ordercreatedate FROM Orders WHERE o_orderkey = :order_id"
        for order_result in app.db.execute(order_query, order_id=order_id):
            order_details['order_number'] = order_result[0]
            order_details['total_price'] = order_result[1]
            order_details['order_date'] = order_result[2].strftime('%b %d, %Y %H:%M:%S')

            break  # Break after the first (and only) iteration

        if not order_details:
            return None  # No order found

        # Fetch the line items for this order
        lineitems_query = """
            SELECT p.p_productname, l.l_quantity, l.l_originalprice, (l.l_quantity * l.l_originalprice) AS subtotal, l_sellerkey
            FROM Lineitem l
            JOIN ProductSeller ps ON l.l_productkey = ps.ps_productkey AND l.l_sellerkey = ps.ps_sellerkey
            JOIN Product p ON ps.ps_productkey = p.p_productkey
            WHERE l.l_orderkey = :order_id
        """
        products = []
        for line_item in app.db.execute(lineitems_query, order_id=order_id):
            products.append({
                'name': line_item[0],
                'quantity': line_item[1],
                'price': line_item[2],
                'subtotal': line_item[3],
                'sellerkey': line_item[4]
            })

        order_details['products'] = products

        return order_details


##### Used in user balance page #####
    @staticmethod
    def get_monthly_expenditure(userkey):
        try:
            rows = app.db.execute("""
                SELECT
                    EXTRACT(YEAR FROM o_ordercreatedate) AS order_year,
                    EXTRACT(MONTH FROM o_ordercreatedate) AS order_month,
                    SUM(o_totalprice) AS total_spent
                FROM Orders
                WHERE
                    o_userkey = :userkey AND
                    o_ordercreatedate >= CURRENT_DATE - INTERVAL '1 year'
                GROUP BY
                    EXTRACT(YEAR FROM o_ordercreatedate),
                    EXTRACT(MONTH FROM o_ordercreatedate)
                ORDER BY
                    order_year,
                    order_month;
                """,
                userkey=userkey)
            # app.logger.info(f"get_monthly_expenditure for {userkey}") 
            # app.logger.info(f"monthly_expenditure: {rows}") 
            return rows if rows else None
        except Exception as e:
            app.logger.error(f"Failed to fetch monthly expenditure for user {userkey}: {str(e)}")
            return None
        
    @staticmethod
    def get_weekly_expenditure(userkey):
        try:
            rows = app.db.execute("""
                SELECT
                    EXTRACT(YEAR FROM o_ordercreatedate) AS order_year,
                    EXTRACT(WEEK FROM o_ordercreatedate) AS order_week,
                    SUM(o_totalprice) AS total_spent
                FROM Orders
                WHERE
                    o_userkey = :userkey AND
                    o_ordercreatedate >= CURRENT_DATE - INTERVAL '1 year'
                GROUP BY
                    EXTRACT(YEAR FROM o_ordercreatedate),
                    EXTRACT(WEEK FROM o_ordercreatedate)
                ORDER BY
                    order_year,
                    order_week;
                """,
                userkey=userkey)
            # app.logger.info(f"get_weekly_expenditure for {userkey}") 
            return rows if rows else None
        except Exception as e:
            app.logger.error(f"Failed to fetch weekly expenditure for user {userkey}: {str(e)}")
            return None
        
    @staticmethod
    def get_user_spending_summary(userkey, startdate, enddate):
        try:
            rows = app.db.execute("""
                SELECT 
                    c.cat_catname AS Category_Name,
                    CAST(SUM((l.l_originalprice - COALESCE(l.l_discount, 0) + COALESCE(l.l_tax, 0)) * l.l_quantity) AS DECIMAL(10,2)) AS Total_Spending_Per_Category
                FROM 
                    Orders o
                JOIN 
                    Lineitem l ON o.o_orderkey = l.l_orderkey
                JOIN 
                    Product p ON l.l_productkey = p.p_productkey
                JOIN 
                    Category c ON p.p_catkey = c.cat_catkey
                WHERE 
                    o.o_userkey = :userkey
                    AND o.o_ordercreatedate BETWEEN :startdate AND :enddate
                GROUP BY 
                    c.cat_catname
                UNION ALL
                SELECT 
                    'Total' AS Category_Name,
                    CAST(SUM(o.o_totalprice) AS DECIMAL(10,2)) AS Total_Spending
                FROM 
                    Orders o
                WHERE 
                    o.o_userkey = :userkey
                    AND o.o_ordercreatedate BETWEEN :startdate AND :enddate;
                """,
                userkey=userkey,
                startdate=startdate,
                enddate=enddate)
            app.logger.info(f"get_user_spending_summary for {userkey}") 
            # app.logger.info(f"{rows}") 
            return rows if rows else None
        except Exception as e:
            app.logger.error(f"Failed to fetch spending_summary for user {userkey}: {str(e)}")
            return None

    @staticmethod
    def get_order_counts(userkey):
        try:
            rows = app.db.execute("""
                SELECT 
                    o_userkey,
                    COUNT(*) AS total_orders,
                    COUNT(o_fulfillmentdate) AS completed_orders,
                    COUNT(*) - COUNT(o_fulfillmentdate) AS in_progress_orders
                FROM 
                    Orders
                WHERE 
                    o_userkey = :userkey
                GROUP BY 
                    o_userkey;
                """,
                userkey=userkey)
            app.logger.info(f"{rows}") 
            if rows:
                return rows[0][1:] 
            else:
                return [0]*3 # has zero order
        except Exception as e:
            app.logger.error(f"Failed to fetch order counts for user {userkey}: {str(e)}")
            return None
##### Used in user_balance #####