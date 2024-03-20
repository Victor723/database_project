from flask import current_app as app


class Product:
    def __init__(self, p_productkey, p_productname, p_price, available):
        self.p_productkey = p_productkey
        self.p_productname = p_productname
        self.p_price = p_price
        self.available = available

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT p_productkey, p_productname, p_price
FROM Product
WHERE p_productkey = :p_productkey
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT p_productkey, p_productname, p_price
FROM Product
''',
                              available=available)
        return [Product(*row) for row in rows]
