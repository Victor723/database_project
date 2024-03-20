from flask import current_app as app


class Product:
    def __init__(self, id, name, price, available):
        self.id = id
        self.name = name
        self.price = price
        self.available = available

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT p_productkey, name, price, available
FROM Product
WHERE p_productkey = :p_productkey
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT p_productkey, name, price, available
FROM Product
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
