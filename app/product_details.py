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

    had_review = ProductReview.get()
    bought = Order.get()
    can_add_review = not had_review & bought
    return render_template('product.html',
                        product_details=product_details,
                        
                        can_add_review=can_add_review)