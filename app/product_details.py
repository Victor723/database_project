from flask import render_template, request
from flask_login import current_user
import datetime

from .models.product import Product
from .models.category import Category

from flask import Blueprint
bp = Blueprint('product_details', __name__)

@bp.route('/product/<int:product_id>')
def product_details(product_id):
    product_details = Product.get_prod_details(product_id)

    if product_details:
        catkey = product_details.p_catkey
        cat = Category.get_catname(catkey)
        if cat:
            cat_name = cat.cat_name  
        else:
            cat_name = "Unknown Category" 
    else:
        return "Product not found", 404

    return render_template('product.html',
                        product_details=product_details,
                        cat_name = cat_name)