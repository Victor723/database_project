from flask import Blueprint
from flask import render_template, redirect, url_for, session
from .models.cart import Cart

bp = Blueprint('cart', __name__)

# @bp.route('/<u_userkey>/cart', methods=['GET'])
# def get_cart(u_userkey):
#     # Retrieve cart items using the userkey from the URL path
#     cart_items = Cart.get_products_by_c_userkey(c_userkey=u_userkey)

#     # Render the cart page with the cart items and user_id
#     return render_template('cart.html', cart_items=cart_items, user_id=u_userkey)

# @bp.route('/shopping-cart')
# def shopping_cart():
#     if 'user_key' not in session:
#         # Handle not logged in
#         return redirect(url_for('users.login'))
        
#     c_userkey = session['user_key']
#     cart_products = Cart.get_incart_products_by_c_userkey(c_userkey)
#     # Assuming that pc_incartquantity > 0 means the item is in the cart
#     cart_items = [product for product in cart_products if product['pc_incartquantity'] > 0]
    
#     return render_template('shopping_cart.html', cart_items=cart_items)

# @bp.route('/save-for-later')
# def save_for_later():
#     if 'user_key' not in session:
#         # Handle not logged in
#         return redirect(url_for('users.login'))
        
#     c_userkey = session['user_key']
#     saved_products = Cart.get_save_products_by_c_userkeys(c_userkey)
#     # Assuming that pc_savequantity > 0 means the item is saved for later
#     saved_items = [product for product in saved_products if product['pc_savequantity'] > 0]
    
#     return render_template('save_for_later.html', saved_items=saved_items)

@bp.route('/<u_userkey>/shopping-cart')
def shopping_cart(u_userkey):

    cart_products = Cart.get_incart_products_by_c_userkey(c_userkey = u_userkey) or []
    # Assuming that pc_incartquantity > 0 means the item is in the cart
    cart_items = [product for product in cart_products if product[4] > 0]
    
    return render_template('shopping_cart.html', cart_items=cart_items)

@bp.route('/<u_userkey>/save-for-later')
def save_for_later(u_userkey):

    saved_products = Cart.get_save_products_by_c_userkey(c_userkey = u_userkey)
    # Assuming that pc_savequantity > 0 means the item is saved for later
    saved_items = [product for product in saved_products if product[4] > 0]
    
    return render_template('save_for_later.html', saved_items=saved_items)