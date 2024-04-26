from flask import Blueprint,jsonify
from flask import render_template, redirect, url_for
from flask import request, redirect, url_for, flash
from .models.cart import Cart
from flask_login import current_user, login_required
bp = Blueprint('cart', __name__)

@bp.route('/shopping-cart/', methods=['GET', 'POST'])
@login_required 
def shopping_cart():
    user_key = current_user.userkey  
    print("User ID:", user_key)
    if request.method == 'POST':
        product_key = request.form.get('product_key')
        seller_key = request.form.get('seller_key')
        new_quantity = int(request.form.get('quantity'))  # Convert quantity to int

        if Cart.update_incart_quantity(user_key, product_key, seller_key, new_quantity):
            flash('Cart updated successfully', 'success')
        else:
            flash('Error updating cart', 'error')

        return redirect(url_for('.shopping_cart'))

    cart_products = Cart.get_incart_products_by_c_userkey(c_userkey = user_key) or []
    # Assuming that pc_incartquantity > 0 means the item is in the cart
    cart_items = [product for product in cart_products if product[4] > 0]
    print(cart_products)

    total_cost = Cart.get_incart_total_cost_by_c_userkey(c_userkey=user_key) or []
    # print(total_cost)
    return render_template('shopping_cart.html', cart_items=cart_items, total_cost = total_cost)

@bp.route('/save-for-later')
@login_required
def save_for_later():
    userkey = current_user.userkey  # Assuming your user model has an 'id' attribute
    print("User ID:", userkey)
    saved_products = Cart.get_save_products_by_c_userkey(c_userkey = userkey) or []
    # Assuming that pc_savequantity > 0 means the item is saved for later
    saved_items = [product for product in saved_products if product[4] > 0]
    
    return render_template('save_for_later.html', saved_items=saved_items)

@bp.route('/update-quantity', methods=['POST'])
@login_required
def update_quantity():
    try:
        data = request.get_json()
        new_quantity = int(data['new_quantity'])
        product_key = data['product_key']
        seller_key = data['seller_key']

        updated_quantity = Cart.update_incart_quantity(current_user.userkey, product_key, seller_key, new_quantity)
        return jsonify({'new_quantity': updated_quantity}), 200
    except TypeError as e:
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500
    except KeyError:
        return jsonify({'error': 'Missing data in request.'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid input. Ensure all inputs are correct.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp.route('/remove-item', methods=['POST'])
@login_required
def remove_item():
    try:
        data = request.get_json()
        product_key = data.get('product_key')
        seller_key = data.get('seller_key')
        user_key = current_user.userkey
  
        success = Cart.remove_item(user_key, product_key, seller_key)
        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Item not found or could not be removed'}), 200
    except KeyError:
        return jsonify({'error': 'Missing necessary data'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp.route('/move-to-save-for-later', methods=['POST', 'GET'])
@login_required
def move_to_save_for_later():
    if request.method == 'GET':
        # Redirect to a different page or show an error message
        return jsonify({'error': 'This URL can only be accessed using POST'}), 405

    try:
        data = request.get_json()
        product_key = data.get('product_key')
        seller_key = data.get('seller_key')

        if Cart.move_to_save_for_later(current_user.userkey, product_key, seller_key):
            return jsonify({'success': 'Item saved for later successfully'}), 200
        else:
            return jsonify({'error': 'Failed to save item for later'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    user_key = current_user.userkey
    cart_key = Cart.get_cartkey_by_user(c_userkey=user_key)
    success = Cart.create_order_from_cart(user_key, cart_key)
    if success:
        return jsonify({'success': 'Order created successfully'}), 200
    else:
        return jsonify({'error': 'Failed to create order'}), 500
