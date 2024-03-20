from flask import current_app as app


class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price
        #self.available = available

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT p_productkey, p_productname, p_price
FROM Product
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT p_productkey, p_productname, p_price
FROM Product
'''
                              )
        return [Product(*row) for row in rows]
