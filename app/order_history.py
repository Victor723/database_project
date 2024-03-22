from flask import render_template, request
from flask_login import current_user
import datetime
from flask import jsonify
from .models.user import User

from flask import Blueprint
bp = Blueprint('order_history', __name__)

@bp.route('/order_history', methods=['GET', 'POST'])
def order_history():
    userkey = None
    order_history_data = []

    if request.method == 'POST':
        userkey = request.form.get('userkey')
        if userkey:
            order_history_data = User.get_order_history_by_id(userkey)

    return render_template('order_history.html',
                    order_history=order_history_data)
