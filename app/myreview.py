from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
import datetime

from .models.productreview import ProductReview
from .models.sellerreview import SellerReview

from flask import Blueprint
bp = Blueprint('myreview', __name__)


@bp.route('/<u_userkey>/myreview', methods=['GET'])
def get_myreview(u_userkey):
    productreviews = ProductReview.get_user_reviews(u_userkey)
    sellerreviews = SellerReview.get_user_reviews(u_userkey)
    # display all reviews written by the user
    return render_template('my_review.html', my_products_reviews = productreviews, my_seller_reviews = sellerreviews)#, my_top5_reviews = top5_reviews)

@bp.route('/delete_product_review/<pr_userkey>/<pr_productkey>', methods=['POST'])
def delete_product_review(pr_userkey, pr_productkey):
    # Assuming a method exists to delete the review based on both keys
    review = ProductReview.get(pr_userkey, pr_productkey)
    if review:
        ProductReview.delete_product_review(pr_userkey, pr_productkey)
        flash('Review successfully deleted.', 'success')
        pass
    return redirect(url_for('myreview.get_myreview', u_userkey=pr_userkey))

@bp.route('/delete_seller_review/<sr_userkey>/<sr_sellerkey>', methods=['POST'])
def delete_seller_review(sr_userkey, sr_sellerkey):
    # Assuming a method exists to delete the review based on both keys
    review = SellerReview.get(sr_userkey, sr_sellerkey)
    if review:
        SellerReview.delete_seller_review(sr_userkey, sr_sellerkey)
        flash('Review successfully deleted.', 'success')
        pass
    return redirect(url_for('myreview.get_myreview', u_userkey=sr_userkey))

@bp.route('/edit_product_review/<pr_userkey>/<pr_productkey>', methods=['GET'])
def edit_product_review(pr_userkey, pr_productkey):
    review = ProductReview.get(pr_userkey, pr_productkey)
    if review:
        return render_template('edit_review.html', review=review, pr_userkey=pr_userkey, pr_productkey=pr_productkey)
    else:
        # Handle the case where the review does not exist
        return redirect(url_for('myreview.get_myreview', u_userkey=pr_userkey))
    
@bp.route('/edit_product_review/<sr_userkey>/<sr_sellerkey>', methods=['GET'])
def edit_seller_review(sr_userkey, sr_sellerkey):
    review = SellerReview.get(sr_userkey, sr_sellerkey)
    if review:
        return render_template('edit_review.html', review=review, sr_userkey=sr_userkey, sr_sellerkey=sr_sellerkey)
    else:
        # Handle the case where the review does not exist
        return redirect(url_for('myreview.get_myreview', u_userkey=sr_userkey))
