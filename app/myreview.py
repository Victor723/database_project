from flask import render_template, request
from flask_login import current_user
import datetime

from .models.productreview import ProductReview
from .models.sellerreview import SellerReview

from flask import Blueprint
bp = Blueprint('myreview', __name__)


@bp.route('/myreview', methods=['GET', 'POST'])
def myreview():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        # get all product reviews from the user:
        productreviews = ProductReview.get_top5_user_reviews(user_id)
        # get all seller reviews from the user:
        sellerreviews = SellerReview.get_top5_user_reviews(user_id)
        # get the most recent five reviews 
        # standardize reviews into a common format: (date, review_object)
        #standardized_reviews = [(review.pr_reviewdate, review) for review in productreviews] + [(review.sr_reviewdate, review) for review in sellerreviews]
        # sort standardized reviews by date in descending order
        #standardized_reviews.sort(key=lambda x: x[0], reverse=True)
        # extract the review objects from the sorted list and get the top 5
        #top5_reviews = [review for _, review in standardized_reviews[:5]]
        # render the page by adding information to the myreviews.html file
        return render_template('myreview.html', my_products_reviews = productreviews, my_seller_reviews = sellerreviews)#, my_top5_reviews = top5_reviews)
    return render_template('myreview.html')