from flask import current_app as app
from app.models.productseller import ProductSeller    
from app.models.seller import Seller
class Order:
    def __init__(self, o_orderkey, o_userkey, o_totalprice, o_ordercreatedate):
        self.o_orderkey = o_orderkey
        self.o_userkey = o_userkey
        self.o_totalprice = o_totalprice
        self.o_ordercreatedate = o_ordercreatedate

    @staticmethod
    def get_orders(o_userkey, offset=0, per_page=10):
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
                :per_page OFFSET :offset;
        '''
        rows = app.db.execute(query, o_userkey=o_userkey, offset=offset, per_page=per_page)
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
            SELECT p.p_productname, u.u_firstname, u.u_lastname, ps_sellerkey ,l.l_quantity, l.l_originalprice, (l.l_quantity * l.l_originalprice) AS subtotal
            FROM Lineitem l
            JOIN ProductSeller ps ON l.l_productkey = ps.ps_productkey AND l.l_sellerkey = ps.ps_sellerkey
            JOIN Product p ON ps.ps_productkey = p.p_productkey
            JOIN Seller s ON s.s_sellerkey = ps.ps_sellerkey
            JOIN Users u ON s.s_userkey = u.u_userkey
            WHERE l.l_orderkey = :order_id
        """
        products = []
        for line_item in app.db.execute(lineitems_query, order_id=order_id):
            products.append({
                'product_name': line_item[0],
                'seller_name': line_item[1] + ' ' + line_item[2],
                'quantity': line_item[4],
                'price': line_item[5],
                'subtotal': line_item[6],
            })

        order_details['products'] = products

        return order_details
