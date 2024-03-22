from flask import current_app as app


class ProductReview:
    def __init__(self, pr_productkey, pr_userkey, pr_productname, pr_orderkey, pr_reviewdate, pr_review, pr_rating):
        self.pr_productkey = pr_productkey
        self.pr_userkey = pr_userkey
        self.pr_productname = pr_productname
        self.pr_orderkey = pr_orderkey
        self.pr_reviewdate = pr_reviewdate
        self.pr_review = pr_review
        self.pr_rating = pr_rating

    @staticmethod
    def get(pr_productkey, pr_userkey):
        rows = app.db.execute('''
SELECT pr_productkey, pr_userkey, pr_productname, pr_orderkey, pr_reviewdate, pr_review, pr_rating
FROM ProductReview
WHERE pr_productkey = :pr_productkey AND pr_userkey = :pr_userkey
''',
                              pr_productkey = pr_productkey, pr_userkey = pr_userkey)
        return ProductReview(*(rows[0])) if rows is not None else None

    
    @staticmethod
    def get_user_reviews(pr_userkey):
        rows = app.db.execute('''
SELECT pr_productkey, pr_userkey, pr_productname, pr_orderkey, pr_reviewdate, pr_review, pr_rating
FROM ProductReview
WHERE pr_userkey = :pr_userkey
ORDER BY pr_reviewdate DESC
''',
                              pr_userkey = pr_userkey)
        return [ProductReview(*row) for row in rows]
    
    @staticmethod
    def get_top5_user_reviews(pr_userkey):
        rows = app.db.execute('''
SELECT pr_productkey, pr_userkey, pr_productname, pr_orderkey, pr_reviewdate, pr_review, pr_rating
FROM ProductReview
WHERE pr_userkey = :pr_userkey
ORDER BY pr_reviewdate DESC
LIMIT 5
''',
                              pr_userkey = pr_userkey)
        return [ProductReview(*row) for row in rows]

