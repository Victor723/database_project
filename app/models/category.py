from flask import current_app as app

class Category:
    def __init__(self, catkey, catname):
        self.catkey = catkey
        self.catname = catname

    @staticmethod
    def get_catname(catkey):
        row = app.db.execute('''
SELECT cat_catname
FROM Category
WHERE cat_catkey = :catkey
''',
                              catkey=catkey)
        return row[0][0] if row else None

    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT cat_catkey, cat_catname
FROM Category
''')
        return [Category(*row) for row in rows]

    def serialize(self):
        return {
            'catkey': self.catkey,
            'catname': self.catname
        }
    
    @staticmethod
    def create_category(catname):
        try:
            app.db.execute('''
                INSERT INTO Category (cat_catname)
                VALUES (:catname)
                ''',
                catname=catname)
            return True
        except Exception as e:
            # Rollback the transaction if there's an error
            app.db.rollback()
            raise e
