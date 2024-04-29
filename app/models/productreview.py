from flask import current_app as app


class ProductReview:
    def __init__(self, pr_productkey, pr_userkey, pr_productname, pr_reviewdate, pr_review, pr_rating):
        self.pr_productkey = pr_productkey
        self.pr_userkey = pr_userkey
        self.pr_productname = pr_productname
        self.pr_reviewdate = pr_reviewdate
        self.pr_review = pr_review
        self.pr_rating = pr_rating

    @staticmethod
    def get(pr_productkey, pr_userkey):
        rows = app.db.execute('''
SELECT pr_productkey, pr_userkey, pr_productname, pr_reviewdate, pr_review, pr_rating
FROM ProductReview
WHERE pr_productkey = :pr_productkey AND pr_userkey = :pr_userkey
''',
                              pr_productkey = pr_productkey, pr_userkey = pr_userkey)
        if rows:
            return ProductReview(*rows[0])
        else:
            return None

    
    @staticmethod
    def get_user_reviews(pr_userkey):
        rows = app.db.execute('''
SELECT pr_productkey, pr_userkey, pr_productname, pr_reviewdate, pr_review, pr_rating
FROM ProductReview
WHERE pr_userkey = :pr_userkey
ORDER BY pr_reviewdate DESC
''',
                              pr_userkey = pr_userkey)
        return [ProductReview(*row) for row in rows]
    
    @staticmethod
    def get_product_reviews(pr_productkey):
        rows = app.db.execute('''
SELECT pr_productkey, pr_userkey, pr_productname, pr_reviewdate, pr_review, pr_rating
FROM ProductReview
WHERE pr_productkey = :pr_productkey
ORDER BY pr_reviewdate DESC
''',
                              pr_productkey = pr_productkey)
        return [ProductReview(*row) for row in rows]
    
    @staticmethod
    def get_product_rating(pr_productkey):
        rows = app.db.execute('''
SELECT ROUND(AVG(pr_rating), 1)
FROM ProductReview
WHERE pr_productkey = :pr_productkey
GROUP BY pr_productkey
''',
                              pr_productkey = pr_productkey)
        if rows:
            return rows[0][0]
        else:
            return 0.0
    
    @staticmethod
    def get_product_review_counts(pr_productkey):
        rows = app.db.execute('''
SELECT COUNT(DISTINCT pr_userkey)
FROM ProductReview
WHERE pr_productkey = :pr_productkey
''',
                              pr_productkey = pr_productkey)
        return rows[0][0]

    @staticmethod
    def get_top5_user_reviews(pr_userkey):
        rows = app.db.execute('''
SELECT pr_productkey, pr_userkey, pr_productname, pr_reviewdate, pr_review, pr_rating
FROM ProductReview
WHERE pr_userkey = :pr_userkey
ORDER BY pr_reviewdate DESC
LIMIT 5
''',
                              pr_userkey = pr_userkey)
        return [ProductReview(*row) for row in rows]
    
    @staticmethod
    def delete_product_review(pr_userkey, pr_productkey):
        app.db.execute('''
DELETE
FROM ProductReview
WHERE pr_productkey = :pr_productkey AND pr_userkey = :pr_userkey
''',
                              pr_userkey = pr_userkey, pr_productkey = pr_productkey)
        
    @staticmethod
    def edit_product_review(pr_userkey, pr_productkey, new_review, new_rating, new_date):
        app.db.execute('''
UPDATE ProductReview
SET pr_review = :new_review, pr_reviewdate = :new_date, pr_rating = :new_rating
WHERE pr_productkey = :pr_productkey AND pr_userkey = :pr_userkey  
''',
                              pr_userkey = pr_userkey, pr_productkey = pr_productkey, new_review = new_review, new_rating = new_rating, new_date = new_date)
        
    @staticmethod
    def new_product_review(pr_productkey, pr_userkey, pr_productname, pr_reviewdate, pr_review, pr_rating):
        app.db.execute('''
INSERT INTO ProductReview(pr_productkey, pr_userkey, pr_productname, pr_reviewdate, pr_review, pr_rating)
VALUES (:pr_productkey, :pr_userkey, :pr_productname, :pr_reviewdate, :pr_review, :pr_rating)
''',
                              pr_productkey = pr_productkey, pr_userkey = pr_userkey, pr_productname = pr_productname, pr_reviewdate = pr_reviewdate, pr_review = pr_review, pr_rating = pr_rating)

