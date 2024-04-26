from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models.order import Order
from datetime import datetime
bp = Blueprint('orders', __name__)

@bp.route('/orders/', methods=['GET'])
@login_required
def display_orders():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    orders, total_orders = Order.get_orders(current_user.userkey, offset)
    total_pages = (total_orders + per_page - 1) // per_page  # Calculate the total number of pages
    
    return render_template('orders.html', orders=orders, page=page, total_pages=total_pages)

    
@bp.route('/order-details/', methods=['GET', 'POST'])
@login_required
def order_details():
    if request.method == 'POST':
        # Retrieve order_id from the form data
        order_id = request.form.get('order_id')
        if order_id:
            order_details = Order.get_order_details(order_id)
            if order_details:
                # Render the order details template with the order data
                return render_template('order_details.html', order_details=order_details)
            else:
                flash('Order not found.', 'error')
                return redirect(url_for('orders.display_orders'))
        else:
            flash('No order ID provided.', 'error')
            return redirect(url_for('orders.display_orders'))
    else:
        flash('Invalid request method.', 'error')
        return redirect(url_for('orders.display_orders'))
