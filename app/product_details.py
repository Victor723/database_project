from flask import render_template, request, redirect, url_for
from flask_login import current_user
import datetime

from .models.product import Product
from .models.cart import Cart
from .models.seller import Seller
from .models.productreview import ProductReview
from .models.productseller import ProductSeller

from flask import Blueprint
bp = Blueprint('product_details', __name__)

@bp.route('/product/<int:product_id>')
def product_details(product_id):
    product_details = Product.get_prod_details(product_id)
    # add review session
    product_reviews = ProductReview.get_product_reviews(product_id)
    
    sellers_ids = ProductSeller.get_sellerkey_by_productkey(product_id)
    productseller_info = []
    for sid in sellers_ids:
        productseller_info.append(ProductSeller.get_product_info(sid, product_id))
    
    if current_user.is_authenticated:
        user_key = current_user.userkey
    else:
        user_key = None

    # had_review = ProductReview.get(user_key, product_id)
    # # bought = Order.get()
    # can_add_review = not had_review # & bought
    return render_template('product.html',
                        product_details=product_details,
                        productseller_info=productseller_info,
                        product_reviews = product_reviews,
                        user_key = user_key)


@bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    productkey = request.form['product_id']
    # Iterate over each seller and check the quantity requested
    if current_user.is_authenticated:
        userkey = current_user.userkey
        for key in request.form:
            if key.startswith('quantity_'):
                sellerkey = key.split('_')[1]
                quantity = int(request.form[key])
                if quantity > 0:
                    # add quantity of product from seller to cart
                    Cart.add_to_cart(userkey, productkey, sellerkey, quantity)
    else:
        return redirect(url_for('users.login'))  # Redirect to the cart page or another appropriate page
    return redirect(url_for('cart.shopping_cart'))  # Redirect to the cart page or another appropriate page
