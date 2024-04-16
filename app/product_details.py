from flask import render_template, request
from flask_login import current_user
import datetime

from .models.product import Product
from .models.category import Category
from .models.seller import Seller
from .models.productreview import ProductReview

from flask import Blueprint
bp = Blueprint('product_details', __name__)

@bp.route('/product/<int:product_id>')
def product_details(product_id):
    product_details = Product.get_prod_details(product_id)
    # add review session
    product_reviews = ProductReview.get_product_reviews(product_id)
    # for test
    
    user_key = current_user.userkey
    

    # had_review = ProductReview.get(user_key, product_id)
    # # bought = Order.get()
    # can_add_review = not had_review # & bought
    return render_template('product.html',
                        product_details=product_details,
                        product_reviews = product_reviews,
                        user_key = user_key)