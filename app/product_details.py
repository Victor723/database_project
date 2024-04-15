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

    catkey = product_details.p_catkey
    catname = Category.get_catname(catkey)


    return render_template('product.html',
                        product_details=product_details,
                        cat_name = catname)