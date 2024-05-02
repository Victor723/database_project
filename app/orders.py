from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models.order import Order
from .models.seller import Seller
from .models.lineitem import Lineitem
from datetime import datetime, timedelta
from flask import current_app

bp = Blueprint('orders', __name__)

@bp.route('/orders/', methods=['GET'])
@login_required
def display_orders():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    mode = request.args.get('mode', 'all')
    time_frame = request.args.get('time_frame', 'all')
    product_name = request.args.get('product_name', '')  # Retrieve product name from query parameters
    
    current_date = datetime.now()
    start_date = None
    end_date = None

    if time_frame == '30_days':
        start_date = current_date - timedelta(days=30)
    elif time_frame == 'three_months':
        start_date = current_date - timedelta(days=90)
    elif time_frame == '2024':
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
    elif time_frame == '2023':
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
    elif time_frame == '2022':
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2022, 12, 31)

    # Convert the product_name to a list if it is not empty
    product_names = [product_name] if product_name else []

    orders, total_orders = Order.get_orders(current_user.user_key, offset, per_page, start_date, end_date, mode, product_names)
    # current_app.logger.info(f'{len(orders)}, {total_orders}')
    total_pages = (total_orders + per_page - 1) // per_page  # Calculate the total number of pages

    return render_template('orders.html', orders=orders, page=page, total_pages=total_pages, 
                           time_frame=time_frame, total_orders=total_orders, mode=mode,
                           product_name=product_name)


    
@bp.route('/order-details/', methods=['GET', 'POST'])
@login_required
def order_details():
    if request.method == 'POST':
        # Retrieve order_id from the form data
        order_id = request.form.get('order_id')
        if order_id:
            order_details = Order.get_order_details(order_id)
            is_fullfilled = Lineitem.is_fulfilled(order_id)
            if(is_fullfilled != False):
                success = Order.update_fulfillment_date(order_id, is_fullfilled)
                if not success:
                    flash('Failed to update the fulfillment date.', 'error')
            fulfilled_date = Order.get_fullfilldate(order_id)
            if order_details:
                user_key = current_user.user_key
                # Render the order details template with the order data
                print(order_details['products'])
                return render_template('order_details.html', order_details=order_details, user_key = user_key)
            else:
                flash('Order not found.', 'error')
                return redirect(url_for('orders.display_orders'))
        else:
            flash('No order ID provided.', 'error')
            return redirect(url_for('orders.display_orders'))
    else:
        flash('Invalid request method.', 'error')
        return redirect(url_for('orders.display_orders'))


@bp.app_context_processor
def inject_user_status():
    if not current_user.is_authenticated:
        return {'is_seller': False}
    is_seller = True if Seller.get_sellerkey(current_user.user_key) else False
    return dict(is_seller=is_seller)