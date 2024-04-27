from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models.order import Order
from .models.seller import Seller
from datetime import datetime, timedelta
from flask import current_app

bp = Blueprint('orders', __name__)

@bp.route('/orders/', methods=['GET'])
@login_required
def display_orders():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    time_frame = request.args.get('time_frame', 'all')
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

    orders, total_orders = Order.get_orders(current_user.userkey, offset, per_page, start_date, end_date)
    current_app.logger.info(f'{len(orders)}, {total_orders}')
    total_pages = (total_orders + per_page - 1) // per_page  # Calculate the total number of pages

    return render_template('orders.html', orders=orders, page=page, total_pages=total_pages, 
                           time_frame=time_frame, total_orders=total_orders,
                           active_tab='all-orders')


@bp.route('/order/pending-orders')
@login_required
def api_pending_orders():
    pending_orders = Order.get_pending_orders(current_user.userkey)  # Your function to fetch pending orders
    return render_template('pending_orders_snippet.html', orders=pending_orders)



    
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


@bp.app_context_processor
def inject_user_status():
    if not current_user.is_authenticated:
        return {'is_seller': False}
    is_seller = True if Seller.get_sellerkey(current_user.userkey) else False
    return dict(is_seller=is_seller)