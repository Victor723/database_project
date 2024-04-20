from flask import Blueprint, render_template, current_app
from sqlalchemy.exc import SQLAlchemyError
import datetime
from .models.user import User
from .models.order import Order
from flask import Blueprint
from flask_login import current_user, login_required
bp = Blueprint('orders', __name__)

@bp.route('/orders/', methods=['GET', 'POST'])
def show_orders():
    # is_seller = Seller.is_seller(current_user.userkey)
    is_seller = True
    userkey = current_user.userkey
    try:
        orders = Order.get_orders(userkey, 0) or []
        current_app.logger.info(f"Orders fetched for user {userkey}: {orders}")
    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error occurred: {str(e)}")
        orders = []  # Fallback to an empty list in case of database error

    if not orders:
        current_app.logger.info("No orders found.")

    return render_template('orders.html', orders=orders, is_seller=is_seller)
