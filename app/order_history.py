from flask import render_template
from flask_login import current_user
import datetime
from flask import jsonify
from .models.user import User

from flask import Blueprint
bp = Blueprint('order_history', __name__)

@bp.route('/order_history')
def order_history():
    userkey = 3
    order_history = User.get_order_history_by_id(userkey)
    return render_template('order_history.html',
                    order_history=order_history)
