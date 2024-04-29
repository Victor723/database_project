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
    per_page = 5  # Number of items per page

    # Get page numbers for product and seller reviews from the query string
    product_page = request.args.get('product_page', 1, type=int)
    seller_page = request.args.get('seller_page', 1, type=int)

    # Fetch all reviews
    all_product_reviews = ProductReview.get_user_reviews(u_userkey)
    all_seller_reviews = SellerReview.get_user_reviews(u_userkey)

    # Implement pagination for each
    productreviews = all_product_reviews[(product_page-1)*per_page : product_page*per_page]
    sellerreviews = all_seller_reviews[(seller_page-1)*per_page : seller_page*per_page]


    total_product_pages = (len(all_product_reviews) + per_page - 1) // per_page
    total_seller_pages = (len(all_seller_reviews) + per_page - 1) // per_page

    return render_template(
        'my_review.html',
        my_products_reviews=productreviews,
        my_seller_reviews=sellerreviews,
        total_product_pages=total_product_pages,
        total_seller_pages=total_seller_pages,
        current_product_page=product_page,
        current_seller_page=seller_page
    )


@bp.route('/delete_product_review/<pr_userkey>/<pr_productkey>', methods=['POST'])
@login_required
def delete_product_review(pr_userkey, pr_productkey):
    # Assuming a method exists to delete the review based on both keys
    review = ProductReview.get(pr_productkey, pr_userkey)
    if review:
        ProductReview.delete_product_review(pr_userkey, pr_productkey)
        flash('Review successfully deleted.', 'success')
        pass
    return redirect(url_for('myreview.get_myreview', u_userkey=pr_userkey))

@bp.route('/delete_seller_review/<sr_userkey>/<sr_sellerkey>', methods=['POST'])
@login_required
def delete_seller_review(sr_userkey, sr_sellerkey):
    # Assuming a method exists to delete the review based on both keys
    review = SellerReview.get(sr_userkey, sr_sellerkey)
    if review:
        SellerReview.delete_seller_review(sr_userkey, sr_sellerkey)
        flash('Review successfully deleted.', 'success')
        pass
    return redirect(url_for('myreview.get_myreview', u_userkey=sr_userkey))

@bp.route('/edit_product_review/<pr_userkey>/<pr_productkey>', methods=['POST'])
@login_required
def edit_product_review(pr_userkey, pr_productkey):
    review = ProductReview.get(pr_productkey, pr_userkey)
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
@login_required
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
@login_required
def new_product_review(pr_userkey, pr_productkey):
    review = ProductReview.get(pr_productkey, pr_userkey)
    if review == None:
        new_review = request.form['userInput']
        new_rating = int(request.form['userRating'])
        new_date = datetime.datetime.now()
        product_name = Product.get_prod_details(pr_productkey).p_productname
        ProductReview.new_product_review(pr_productkey, pr_userkey, product_name, new_date, new_review, new_rating)
        flash('Review successfully added.', 'success')
        return redirect(url_for('product_details.product_details', product_id=pr_productkey))
    else:
        # Handle the case where the review does not exist
        flash('Review already exists.', 'fail')
        return redirect(url_for('myreview.get_myreview', u_userkey=pr_userkey))
    
@bp.route('/new_seller_review/<sr_userkey>/<sr_sellerkey>', methods=['POST'])
@login_required
def new_seller_review(sr_userkey, sr_sellerkey):
    review = SellerReview.get(sr_userkey, sr_sellerkey)
    if review == None:
        new_review = request.form['userInput']
        new_rating = int(request.form['userRating'])
        new_date = datetime.datetime.now()
        seller_name = Seller.get_seller_information(sr_sellerkey)[0]['first_name']
        print(seller_name)
        SellerReview.new_seller_review(sr_sellerkey, sr_userkey, seller_name, new_date, new_review, new_rating)
        flash('Review successfully updated.', 'success')
        return redirect(url_for('myreview.get_myreview', u_userkey=sr_userkey))
    else:
        # Handle the case where the review does not exist
        flash('Review already exists.', 'fail')
        return redirect(url_for('myreview.get_myreview', u_userkey=sr_userkey))
