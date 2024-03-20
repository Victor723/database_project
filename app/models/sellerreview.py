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
    def get(sr_sellerkey, sr_userkey):
        rows = app.db.execute('''
SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_orderkey, sr_reviewdate, sr_review, sr_rating
FROM SellerReview
WHERE sr_sellerkey = :sr_sellerkey AND sr_userkey = :sr_userkey
''',
                              sr_sellerkey = sr_sellerkey, sr_userkey = sr_userkey)
        return SellerReview(*(rows[0])) if rows is not None else None

    
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

