from flask import Blueprint, jsonify, render_template, flash, request
from .models.cart import Cart
from .models.productseller import ProductSeller
from .models.user import User
from .models.productcart import ProductCart
from .models.order import Order
from flask_login import current_user, login_required
from decimal import Decimal, ROUND_HALF_UP

bp = Blueprint('cart', __name__)

@bp.route('/shopping-cart/', methods=['GET', 'POST'])
@login_required
def shopping_cart():
    user_key = current_user.user_key
    cart_key = Cart.get_or_create_cartkey_by_user(c_userkey=user_key)
    cart_items = Cart.get_incart_products_by_userkey(user_key)
    check_incart_quantity(cart_key, cart_items)
    total_cost = sum(item['subtotal'] for item in cart_items)  # Calculate total cost from subtotals
    return render_template('shopping_cart.html', cart_items=cart_items, total_cost=total_cost)

@bp.route('/save-for-later')
@login_required
def save_for_later():
    userkey = current_user.user_key  # Assuming your user model has an 'id' attribute
    cart_key = Cart.get_or_create_cartkey_by_user(c_userkey=userkey)
    saved_products = Cart.get_save_products_by_c_userkey(c_userkey = userkey) or []
    # Assuming that pc_savequantity > 0 means the item is saved for later
    saved_items = [product for product in saved_products if product['pc_savequantity'] > 0]

    for item in saved_items:
        product_key = item['product_key']
        seller_key = item['seller_key']
        save_quantity = ProductCart.get_incart_quantity(cart_key, product_key, seller_key)
        has_inventory, message = check_inventory(seller_key, product_key, save_quantity)
        if not has_inventory:
            flash(f'Only {message} Please update the quantity.', 'warning')
    return render_template('save_for_later.html', saved_items=saved_items)

@bp.route('/update-incart-quantity', methods=['POST'])
@login_required
def update_incart_quantity():
    """Update the quantity of an item in the shopping cart."""
    try:
        data = request.get_json()
        new_quantity = int(data['new_quantity'])
        product_key = data['product_key']
        seller_key = data['seller_key']
        cart_key = Cart.get_or_create_cartkey_by_user(c_userkey=current_user.user_key)
        has_inventory, message = check_inventory(seller_key, product_key, new_quantity)
        if has_inventory:
            ProductCart.update_incart_quantity(cart_key, product_key, seller_key, new_quantity)
            return jsonify({'new_quantity': new_quantity}), 200
        else:
            return jsonify({'error': message}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/update-save-quantity', methods=['POST'])
@login_required
def update_save_quantity():
    """Update the quantity of an item saved for later."""
    try:
        data = request.get_json()
        new_quantity = int(data['new_quantity'])
        product_key = data['product_key']
        seller_key = data['seller_key']
        cart_key = Cart.get_or_create_cartkey_by_user(c_userkey=current_user.user_key)
        has_inventory, message = check_inventory(seller_key, product_key, new_quantity)
        if has_inventory:
            ProductCart.update_save_quantity(cart_key, product_key, seller_key, new_quantity)
            return jsonify({'new_quantity': new_quantity}), 200
        else:
            return jsonify({'error': message}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/remove-item', methods=['POST'])
@login_required
def remove_item():
    """Remove an item from the shopping cart or saved for later."""
    try:
        data = request.get_json()
        product_key = data.get('product_key')
        seller_key = data.get('seller_key')
        cart_key = Cart.get_or_create_cartkey_by_user(c_userkey=current_user.user_key)
        success = ProductCart.remove_item(cart_key, product_key, seller_key)
        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Item not found or could not be removed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/move-to-save-for-later', methods=['POST', 'GET'])
@login_required
def move_to_save_for_later():
    """Move an item from the cart to save for later."""
    if request.method == 'GET':
        return jsonify({'error': 'This URL can only be accessed using POST'}), 405

    try:
        data = request.get_json()
        product_key = data.get('product_key')
        seller_key = data.get('seller_key')
        cart_key = Cart.get_or_create_cartkey_by_user(c_userkey=current_user.user_key)
        new_quantity = ProductCart.get_incart_quantity(cart_key, product_key, seller_key) + ProductCart.get_save_quantity(cart_key, product_key, seller_key)

        has_inventory, message = check_inventory(seller_key, product_key, new_quantity)
        if has_inventory:
            if ProductCart.move_to_save_for_later(cart_key, product_key, seller_key):
                # flash('Item moved to Save for Later successfully.', 'success')
                return jsonify({'success': 'Item moved to Save for Later successfully'}), 200
            else:
                return jsonify({'error': 'Failed to move item to Save for Later'}), 400
        else:
            return jsonify({'error': message}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/move-to-incart', methods=['POST', 'GET'])
@login_required
def move_to_incart():
    """Move an item from saved for later back to the shopping cart."""
    if request.method == 'GET':
        return jsonify({'error': 'This URL can only be accessed using POST'}), 405

    try:
        data = request.get_json()
        product_key = data.get('product_key')
        seller_key = data.get('seller_key')
        cart_key = Cart.get_or_create_cartkey_by_user(c_userkey=current_user.user_key)
        new_quantity = ProductCart.get_incart_quantity(cart_key, product_key, seller_key) + ProductCart.get_save_quantity(cart_key, product_key, seller_key)

        has_inventory, message = check_inventory(seller_key, product_key, new_quantity)
        if has_inventory:
            if ProductCart.move_to_incart(cart_key, product_key, seller_key):
                # flash('Item moved to cart successfully.', 'success')
                return jsonify({'success': 'Item moved to cart successfully'}), 200
            else:
                return jsonify({'error': 'Failed to move to cart'}), 400
        else:
            return jsonify({'error': message}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    user_key = current_user.user_key
    cart_key = Cart.get_or_create_cartkey_by_user(c_userkey=user_key)
    cart_items = Cart.get_incart_products_by_userkey(user_key)
    check_incart_quantity(cart_key, cart_items)
    total_cost = Cart.get_incart_total_cost_by_c_userkey(c_userkey=user_key)
    total_cost = Decimal(total_cost)
    rounded_cost = total_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    # print(f'Rounded cost: {rounded_cost}')
    has_balance, message = check_balance(user_key, rounded_cost)
    if has_balance: 
        if User.update_balance(user_key, -rounded_cost):
            if Cart.create_order_from_cart(user_key, cart_key):
                new_balance = User.get_balance(user_key)
                # print(f'Order created successfully! Your new balance is ${new_balance:.2f}')
                return jsonify({'success': f'Order created successfully! Your new balance is ${new_balance:.2f}'}), 200
            else:
                return jsonify({'error': 'Failed to create order'}), 500
            
        else:
            return jsonify({'error': 'Failed to update balance'}), 500
        
    else:
        return jsonify({'error': message}), 200

def check_inventory(seller_key, product_key, quantity):
    """Check if enough inventory exists for a given product and seller."""
    product_info = ProductSeller.get_product_info(seller_key, product_key)
    inventory = product_info['quantity'] if product_info else 0
    if inventory >= quantity:
        return True, ''  # Sufficient inventory
    else:
        return False, f"This seller has only {inventory} of these available."

def check_balance(user_key, total_cost):
    """Check if the user has sufficient balance to cover the cost."""
    balance = User.get_balance(user_key)
    if balance >= total_cost:
        return True, ''  # Sufficient balance
    else:
        return False, f"Your current balance is ${balance:.2f}, which is insufficient to cover the total cost of ${total_cost:.2f}."

def check_incart_quantity(cart_key, cart_items):
    """Verify the quantities in the cart against the inventory."""
    for item in cart_items:
        product_key = item['product_key']
        seller_key = item['seller_key']
        incart_quantity = item['pc_incartquantity']
        has_inventory, message = check_inventory(seller_key, product_key, incart_quantity)
        if not has_inventory:
            product_info = ProductSeller.get_product_info(seller_key, product_key)
            inventory = product_info['quantity'] if product_info else 0
            if inventory == 0:
                ProductCart.remove_item(cart_key, product_key, seller_key)
                flash(f"The quantity of {product_info['productname']} with seller {product_info['sellername']} has been removed from your cart as it is no longer available.", 'warning')
            else:
                ProductCart.update_incart_quantity(cart_key, product_key, seller_key, inventory)
                flash(f"{message} The quantity of {product_info['productname']} with seller {product_info['sellername']} has been updated to {inventory}.", 'warning')
