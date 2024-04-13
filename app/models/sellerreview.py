from flask import current_app as app


class SellerReview:
    def __init__(self, sr_sellerkey, sr_userkey, sr_sellername, sr_orderkey, sr_reviewdate, sr_review, sr_rating):
        self.sr_sellerkey = sr_sellerkey
        self.sr_userkey = sr_userkey
        self.sr_sellername = sr_sellername
        self.sr_orderkey = sr_orderkey
        self.sr_reviewdate = sr_reviewdate
        self.sr_review = sr_review
        self.sr_rating = sr_rating

    @staticmethod
    def get(sr_userkey, sr_sellerkey):
        rows = app.db.execute('''
SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_orderkey, sr_reviewdate, sr_review, sr_rating
FROM SellerReview
WHERE sr_sellerkey = :sr_sellerkey AND sr_userkey = :sr_userkey
''',
                              sr_sellerkey = sr_sellerkey, sr_userkey = sr_userkey)
        if rows:
            return SellerReview(*rows[0])
        else:
            return None

    
    @staticmethod
    def get_user_reviews(sr_userkey):
        rows = app.db.execute('''
SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_orderkey, sr_reviewdate, sr_review, sr_rating
FROM SellerReview
WHERE sr_userkey = :sr_userkey
ORDER BY sr_reviewdate DESC
''',
                              sr_userkey = sr_userkey)
        return [SellerReview(*row) for row in rows]

    @staticmethod
    def get_top5_user_reviews(sr_userkey):
        rows = app.db.execute('''
SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_orderkey, sr_reviewdate, sr_review, sr_rating
FROM SellerReview
WHERE sr_userkey = :sr_userkey
ORDER BY sr_reviewdate DESC
LIMIT 5
''',
                              sr_userkey = sr_userkey)
        return [SellerReview(*row) for row in rows]
    
    @staticmethod
    def get_seller_reviews(sr_sellerkey):
        rows = app.db.execute('''
SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_orderkey, sr_reviewdate, sr_review, sr_rating
FROM SellerReview
WHERE sr_usellerkey = :sr_sellerkey
ORDER BY sr_reviewdate DESC
''',
                              sr_sellerkey = sr_sellerkey)
        return [SellerReview(*row) for row in rows]
    
    @staticmethod
    def get_seller_reviews(sr_sellerkey):
        rows = app.db.execute('''
SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_orderkey, sr_reviewdate, sr_review, sr_rating
FROM SellerReview
WHERE sr_usellerkey = :sr_sellerkey
ORDER BY sr_reviewdate DESC
''',
                              sr_sellerkey = sr_sellerkey)
        return [SellerReview(*row) for row in rows]
    
    @staticmethod
    def delete_seller_review(sr_userkey, sr_sellerkey):
        app.db.execute('''
DELETE
FROM SellerReview
WHERE sr_userkey = :sr_userkey AND sr_sellerkey = :sr_sellerkey
''',
                              sr_userkey = sr_userkey, sr_sellerkey = sr_sellerkey)

