from flask import current_app as app


class Product:
    def __init__(self, p_productkey, p_productname, p_price):
        self.p_productkey = p_productkey
        self.p_productname = p_productname
        self.p_price = p_price

    @staticmethod
    def get(p_productkey):
        rows = app.db.execute('''
SELECT p_productkey, p_productname, p_price
FROM Product
WHERE p_productkey = :p_productkey
''',
                              p_productkey=p_productkey)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT p_productkey, p_productname, p_price
FROM Product
''')
        return [Product(*row) for row in rows]

    @staticmethod
    def get_top_K(k):
        rows = app.db.execute(f'''
SELECT p_productkey, p_productname, p_price
FROM Product
ORDER BY p_price DESC
LIMIT {k};
''')
        return [Product(*row) for row in rows]
