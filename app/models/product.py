from flask import current_app as app

class Product:
    def __init__(self, p_productkey, p_productname, p_price, p_catname, p_description=None, p_imageurl=None, p_rating=None, p_discount=None):
        self.p_productkey = p_productkey
        self.p_productname = p_productname
        self.p_price = p_price
        self.p_description = p_description
        self.p_imageurl = p_imageurl 
        self.p_catname = p_catname
        self.p_rating = p_rating


    @staticmethod
    def get_prod_details(p_productkey):
        rows = app.db.execute('''
SELECT p_productkey, p_productname, p_price, cat_catname, p_description, p_imageurl
FROM Product, Category
WHERE p_productkey = :p_productkey
''',
                      p_productkey=p_productkey)
        return Product(*(rows[0])) if rows is not None else None
    

    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT p_productkey, p_productname, p_price, cat_catname, p_description, p_imageurl
FROM Product, Category
WHERE p_catkey = cat_catkey
''')
        return [Product(*row) for row in rows]


    @staticmethod
    def get_top_K(k):
        rows = app.db.execute(f'''
SELECT p_productkey, p_productname, p_price, cat_catname, p_description, p_imageurl
FROM Product, Category
WHERE p_catkey = cat_catkey
ORDER BY p_price DESC
LIMIT {k};
''')
        return [Product(*row) for row in rows]


    @staticmethod
    def get_all_sort_by_price(available=True):
        query = app.db.execute('''
        SELECT COUNT(*)
        FROM Product
        ''')
        product_total = query[0][0]
        return Product.get_top_K(product_total)
    

    @staticmethod
    def get_all_by_category(catkey):
        rows = app.db.execute(f'''
SELECT p_productkey, p_productname, p_price, cat_catname, p_description, p_imageurl
FROM Product, Category
WHERE p_catkey = cat_catkey AND p_catkey = :catkey
''',
            catkey=catkey)
        return [Product(*row) for row in rows]


    @staticmethod
    def get_all_by_keyword(keyword):
        like_pattern = f'%{keyword}%'
        rows = app.db.execute(f'''
SELECT p_productkey, p_productname, p_price, cat_catname, p_description, p_imageurl
FROM Product, Category
WHERE p_catkey = cat_catkey
AND (p_productname LIKE :like_pattern OR p_description LIKE :like_pattern)''', 
            like_pattern=like_pattern)
        return [Product(*row) for row in rows]


    def find_max_productkey():
        row = app.db.execute('''
            SELECT MAX(p_productkey)
            FROM Product
        ''')
        return row[0][0] if row is not None else None


    @staticmethod
    def search_products_by_name(search_query):
        try:
            # Perform a search based on the search query
            # This query will search for similar product names in the Product table
            search_results = app.db.execute(
                """
                SELECT p_productkey, p_productname, p_price, p_description, p_imageurl, p_catkey, cat_catname
                FROM Product, Category
                WHERE p_catkey = cat_catkey AND p_productname LIKE :search_query
                """,
                search_query=f'%{search_query}%'
            )
            return search_results
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    @staticmethod
    def create_product(product_key, product_name, product_price, product_description, product_image_url, category_key):
        app.db.execute(
                """
                INSERT INTO Product (p_productkey, p_productname, p_price, p_description, p_imageurl, p_catkey)
                VALUES (:product_key, :product_name, :product_price, :product_description, :product_image_url, :category_key)
                """,
                product_key=product_key,
                product_name=product_name,
                product_price=product_price,
                product_description=product_description,
                product_image_url=product_image_url,
                category_key=category_key
        )