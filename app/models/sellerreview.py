from flask import current_app as app


class SellerReview:
    def __init__(self, sr_sellerkey, sr_userkey, sr_sellername, sr_reviewdate, sr_review, sr_rating):
        self.sr_sellerkey = sr_sellerkey
        self.sr_userkey = sr_userkey
        self.sr_sellername = sr_sellername
        self.sr_reviewdate = sr_reviewdate
        self.sr_review = sr_review
        self.sr_rating = sr_rating

    @staticmethod
    def get(sr_userkey, sr_sellerkey):
        rows = app.db.execute('''
SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_reviewdate, sr_review, sr_rating
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
SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_reviewdate, sr_review, sr_rating
FROM SellerReview
WHERE sr_userkey = :sr_userkey
ORDER BY sr_reviewdate DESC
''',
                              sr_userkey = sr_userkey)
        return [SellerReview(*row) for row in rows]

    @staticmethod
    def get_top5_user_reviews(sr_userkey):
        rows = app.db.execute('''
SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_reviewdate, sr_review, sr_rating
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
SELECT sr_sellerkey, sr_userkey, sr_sellername, sr_reviewdate, sr_review, sr_rating
FROM SellerReview
WHERE sr_sellerkey = :sr_sellerkey
ORDER BY sr_reviewdate DESC
''',
                              sr_sellerkey = sr_sellerkey)
        return [SellerReview(*row) for row in rows]
    
    @staticmethod
    def get_seller_rating(sr_sellerkey):
        rows = app.db.execute('''
SELECT ROUND(AVG(sr_rating), 2)
FROM SellerReview
WHERE sr_sellerkey = :sr_sellerkey
GROUP BY sr_sellerkey
''',
                              sr_sellerkey = sr_sellerkey)
        if rows:
            return rows[0]
        else:
            return 0
    
    @staticmethod
    def get_seller_review_counts(sr_sellerkey):
        rows = app.db.execute('''
SELECT COUNT(*)
FROM SellerReview
WHERE sr_sellerkey = :sr_sellerkey
''',
                              sr_sellerkey = sr_sellerkey)
        return rows[0]
    
    
    @staticmethod
    def delete_seller_review(sr_userkey, sr_sellerkey):
        app.db.execute('''
DELETE
FROM SellerReview
WHERE sr_userkey = :sr_userkey AND sr_sellerkey = :sr_sellerkey
''',
                              sr_userkey = sr_userkey, sr_sellerkey = sr_sellerkey)
        
    @staticmethod
    def edit_seller_review(sr_userkey, sr_sellerkey, new_review, new_rating, new_date):
        app.db.execute('''
UPDATE SellerReview
SET sr_review = :new_review, sr_reviewdate = :new_date, sr_rating = :new_rating
WHERE sr_sellerkey = :sr_sellerkey AND sr_userkey = :sr_userkey  
''',
                              sr_userkey = sr_userkey, sr_sellerkey = sr_sellerkey, new_review = new_review, new_rating = new_rating, new_date = new_date)
        
    @staticmethod
    def new_seller_review(sr_sellerkey, sr_userkey, sr_sellername, sr_reviewdate, sr_review, sr_rating):
        app.db.execute('''
INSERT INTO ProductReview(sr_sellerkey, sr_userkey, sr_sellername, sr_reviewdate, sr_review, sr_rating)
VALUES (:sr_sellerkey, :sr_userkey, :sr_sellername, :sr_reviewdate, :sr_review, :sr_rating)
''',
                              sr_sellerkey = sr_sellerkey, sr_userkey = sr_userkey, sr_sellername = sr_sellername, sr_reviewdate = sr_reviewdate, sr_review = sr_review, sr_rating = sr_rating)


