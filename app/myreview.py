from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
import datetime

from .models.productreview import ProductReview
from .models.sellerreview import SellerReview
from .models.product import Product
from .models.seller import Seller

from flask import Blueprint
bp = Blueprint('myreview', __name__)


@bp.route('/myreview', methods=['GET'])
@login_required
def get_myreview():
    u_userkey = current_user.userkey
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

@bp.route('/edit_product_review/<pr_userkey>/<pr_productkey>', methods=['POST'])
def edit_product_review(pr_userkey, pr_productkey):
    review = ProductReview.get(pr_userkey, pr_productkey)
    if review:
        new_review = request.form['userInput']
        new_rating = int(request.form['userRating'])
        new_date = datetime.datetime.now()
        # Add new product review
        ProductReview.edit_product_review(pr_userkey, pr_productkey, new_review, new_rating, new_date)
        flash('Review successfully updated.', 'success')
        return redirect(url_for('myreview.get_myreview', u_userkey=pr_userkey))
    else:
        # Handle the case where the review does not exist
        return redirect(url_for('myreview.get_myreview', u_userkey=pr_userkey))
    
@bp.route('/edit_seller_review/<sr_userkey>/<sr_sellerkey>', methods=['POST'])
def edit_seller_review(sr_userkey, sr_sellerkey):
    review = SellerReview.get(sr_userkey, sr_sellerkey)
    if review:
        new_review = request.form['userInput']
        new_rating = int(request.form['userRating'])
        new_date = datetime.datetime.now()
        # Add new product review
        SellerReview.edit_seller_review(sr_userkey, sr_sellerkey, new_review, new_rating, new_date)
        flash('Review successfully updated.', 'success')
        return redirect(url_for('myreview.get_myreview', u_userkey=sr_userkey))
    else:
        # Handle the case where the review does not exist
        return redirect(url_for('myreview.get_myreview', u_userkey=sr_userkey))

@bp.route('/new_product_review/<pr_userkey>/<pr_productkey>', methods=['POST'])
def new_product_review(pr_userkey, pr_productkey):
    review = ProductReview.get(pr_userkey, pr_productkey)
    if review == None:
        new_review = request.form['userInput']
        new_rating = int(request.form['userRating'])
        new_date = datetime.datetime.now()
        product_name = Product.get_prod_details(pr_userkey).p_productname
        ProductReview.new_product_review(pr_productkey, pr_userkey, product_name, new_date, new_review, new_rating)
        flash('Review successfully added.', 'success')
        return redirect(url_for('product_details.product_details', product_id=pr_productkey))
    else:
        # Handle the case where the review does not exist
        flash('Review already exists.', 'fail')
        return redirect(url_for('myreview.get_myreview', u_userkey=pr_userkey))
    
@bp.route('/new_seller_review/<sr_userkey>/<sr_sellerkey>', methods=['POST'])
def new_seller_review(sr_userkey, sr_sellerkey):
    review = SellerReview.get(sr_userkey, sr_sellerkey)
    if review == None:
        new_review = request.form['userInput']
        new_rating = int(request.form['userRating'])
        new_date = datetime.datetime.now()
        seller_name = Seller.get_seller_information(sr_sellerkey).first_name
        SellerReview.new_seller_review(sr_sellerkey, sr_userkey, seller_name, new_date, new_review, new_rating)
        flash('Review successfully updated.', 'success')
        return redirect(url_for('myreview.get_myreview', u_userkey=sr_userkey))
    else:
        # Handle the case where the review does not exist
        return redirect(url_for('myreview.get_myreview', u_userkey=sr_userkey))
