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
