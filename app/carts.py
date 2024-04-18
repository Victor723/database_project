from flask import Blueprint
from flask import render_template, redirect, url_for, session
from flask import request, redirect, url_for, flash
from .models.cart import Cart
from flask_login import current_user, login_required
bp = Blueprint('cart', __name__)

# @bp.route('/<u_userkey>/cart', methods=['GET'])
# def get_cart(u_userkey):
#     # Retrieve cart items using the userkey from the URL path
#     cart_items = Cart.get_products_by_c_userkey(c_userkey=u_userkey)

#     # Render the cart page with the cart items and user_id
#     return render_template('cart.html', cart_items=cart_items, user_id=u_userkey)

@bp.route('/shopping-cart/', methods=['GET', 'POST'])
@login_required 
def shopping_cart():
    user_id = current_user.userkey  # Assuming your user model has an 'id' attribute
    print("User ID:", user_id)
    if request.method == 'POST':
        product_key = request.form.get('product_key')
        seller_key = request.form.get('seller_key')
        new_quantity = int(request.form.get('quantity'))  # Convert quantity to int

        # Here you would get the actual cart_key for the user, this is just a placeholder
        cart_key = Cart.get_cart_key_by_userkey(user_id)  # Implement this function

        if Cart.update_quantity(cart_key, product_key, seller_key, new_quantity):
            flash('Cart updated successfully', 'success')
        else:
            flash('Error updating cart', 'error')

        return redirect(url_for('.shopping_cart'))

    cart_products = Cart.get_incart_products_by_c_userkey(c_userkey = user_id) or []
    # Assuming that pc_incartquantity > 0 means the item is in the cart
    cart_items = [product for product in cart_products if product[4] > 0]
    total_cost = Cart.get_incart_total_cost_by_c_userkey(c_userkey=user_id) or []
    # print(total_cost)
    return render_template('shopping_cart.html', cart_items=cart_items, total_cost = total_cost)

@bp.route('/save-for-later/')
@login_required
def save_for_later():
    userkey = current_user.userkey  # Assuming your user model has an 'id' attribute
    print("User ID:", userkey)
    saved_products = Cart.get_save_products_by_c_userkey(c_userkey = userkey) or []
    # Assuming that pc_savequantity > 0 means the item is saved for later
    saved_items = [product for product in saved_products if product[4] > 0]
    
    return render_template('save_for_later.html', saved_items=saved_items)