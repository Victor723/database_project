from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
from .models.cart import Cart

bp = Blueprint('cart', __name__)

# @bp.route('/carts', methods=['GET', 'POST'])
# def carts():
#     if request.method == 'POST':
#         # Get the user ID from the form submission
#         user_id = request.form.get('user_id')
#         cart_items = Cart.get_products_by_c_userkey(c_userkey=user_id)
#         return render_template('cart.html', cart_items=cart_items, user_id=user_id)
    
#     # On a GET request, just render the page with the form
#     return render_template('cart.html')

@bp.route('/<u_userkey>/cart', methods=['GET'])
def get_cart(u_userkey):
    # Retrieve cart items using the userkey from the URL path
    cart_items = Cart.get_products_by_c_userkey(c_userkey=u_userkey)

    # Render the cart page with the cart items and user_id
    return render_template('cart.html', cart_items=cart_items, user_id=u_userkey)