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
    def get_products_by_c_userkey(c_userkey):
        rows = app.db.execute('''
SELECT p.p_productname,
    u.u_firstname,
    u.u_lastname,
    ps.ps_price,
    pc.pc_savequantity,
    pc.pc_incartquantity
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
