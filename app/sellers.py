from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.seller import Seller


from flask import Blueprint
bp = Blueprint('sellers', __name__)

@bp.route('/seller/login/<u_userkey>', methods=['GET', 'POST'])
def seller_login(u_userkey):
    # Fetch the user's name and corresponding seller key
    seller_key = Seller.get_sellerkey(u_userkey)
    return "login", 400


@bp.route('/seller/<s_sellerkey>', methods=['GET', 'POST'])
def seller_homepage(s_sellerkey):
    # user = User.get_user(u_userkey)
    # Extract the user's/seller's name
    # seller_name = f"{user.u_firstname} {user.u_lastname}" if user else None 
    
    seller_name = "Zero"

    # Render the HTML template with the fetched data
    return render_template('seller_homepage.html', seller_name=seller_name, seller_key=s_sellerkey)


@bp.route('/seller/<s_sellerkey>/inventory', methods=['GET', 'POST'])
def seller_inventory(s_sellerkey):
    # Get product information for the specified sellerkey
    product_info = Seller.get_product_info(s_sellerkey)
    
    # Render the template with the product information
    return render_template('seller_inventory.html', product_info=product_info)


@bp.route('/seller/<s_sellerkey>/order', methods=['GET', 'POST'])
def seller_order(s_sellerkey):
    # Get order information for the specified sellerkey
    order_info = Seller.get_order_info(s_sellerkey)
    
    # Render the template with the order information
    return render_template('seller_order.html', order_info=order_info)


@bp.route('/seller/<s_sellerkey>/review', methods=['GET', 'POST'])
def seller_review(s_sellerkey):
    seller_review = Seller.get_seller_review(s_sellerkey)
    return render_template('seller_review.html',seller_review=seller_review)




