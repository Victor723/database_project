from flask import render_template, redirect, url_for, flash, request, jsonify
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask import current_app as app
from datetime import datetime

from .models.seller import Seller
from .models.productseller import ProductSeller
from .models.sellerreview import SellerReview
from .models.product import Product
from .models.category import Category


from flask import Blueprint
bp = Blueprint('sellers', __name__)


@bp.route('/seller/<s_sellerkey>', methods=['GET', 'POST'])
@login_required
def seller_homepage(s_sellerkey):
    user_info = Seller.get_seller_information(s_sellerkey)
    # Check if user_info is not empty and contains user's name
    if user_info:
        seller_name = user_info[0]['first_name'] + user_info[0]['last_name']
    else:
        # Handle case where user_info is empty or invalid seller key
        seller_name = "User Not Found"
    # Render the HTML template with the fetched data
    return render_template('seller_homepage.html', seller_name=seller_name, seller_key=s_sellerkey)


@bp.route('/seller/<s_sellerkey>/inventory', methods=['GET', 'POST'])
@login_required
def seller_inventory(s_sellerkey):
    # Get the current page from the query parameters or default to page 1
    page = int(request.args.get('page', 1))

    # Define the number of products per page
    products_per_page = 10

    # Get sorting parameters from the request
    sort_column = request.args.get('sort_column', 'ps.ps_productkey')  # Default sorting by product key
    sort_order = request.args.get('sort_order', 'asc')  # Default sorting order is ascending

    # Get the search query from the request
    search_query = request.args.get('search_query', '')

    # If search query is provided, filter products by name or key
    if search_query:
        productseller_info = Seller.search_products(s_sellerkey, search_query)
    else:
        # Calculate the offset for the query based on the current page
        offset = (page - 1) * products_per_page

        # Get product information for the specified sellerkey, limited by pagination and sorted
        productseller_info = Seller.get_product_info_sorted(s_sellerkey, sort_column, sort_order, limit=products_per_page, offset=offset)

    # Calculate the total number of products
    total_products = Seller.get_total_product_count(s_sellerkey)

    # Calculate the total number of pages
    total_pages = (total_products + products_per_page - 1) // products_per_page

    # Render the template with the product information and pagination details

    return render_template('seller_inventory.html', seller_key=s_sellerkey, product_info=product_info, current_page=page, total_pages=total_pages)


@bp.route('/seller/<s_sellerkey>/order', methods=['GET', 'POST'])
@login_required
def seller_order(s_sellerkey):
    # Get the current page from the query parameters or default to page 1
    page = int(request.args.get('page', 1))

    # Define the number of orders per page
    orders_per_page = 10

    # Get sorting parameters from the query string
    date_order = request.args.get('date_order', 'DESC')
    status_order = request.args.get('status_order', 'DESC')

    # Get the search query from the request
    search_query = request.args.get('search_query', '')

    # If search query is provided, filter orders by customer name, product name, or order ID
    if search_query:
        order_info = Seller.search_lineitems(s_sellerkey, search_query)
    else:
        # Calculate the offset for the query based on the current page
        offset = (page - 1) * orders_per_page

        # Get order information for the specified seller key, limited by pagination and sorted
        order_info = Seller.get_order_info(s_sellerkey, limit=orders_per_page, offset=offset, date_order=date_order, status_order=status_order)

    # Calculate the total number of orders
    total_orders = Seller.get_total_order_count(s_sellerkey)

    # Calculate the total number of pages
    total_pages = (total_orders + orders_per_page - 1) // orders_per_page

    # Render the template with the order information, pagination details, and sort order
    return render_template('seller_order.html', seller_key=s_sellerkey, order_info=order_info, current_page=page, total_pages=total_pages, date_order=date_order, status_order=status_order)


@bp.route('/seller/<s_sellerkey>/<o_orderkey>/<l_linenumber>/detail', methods=['GET', 'POST'])
@login_required
def order_details(s_sellerkey, o_orderkey, l_linenumber):
    # Get lineitem information
    lineitem_info = Seller.get_lineitem_info(s_sellerkey, o_orderkey, l_linenumber)
    # Render the template with the product information
    return render_template('seller_order_details.html', lineitem_info=lineitem_info, seller_key=s_sellerkey)


@bp.route('/seller/<s_sellerkey>/<o_orderkey>/<l_linenumber>/finish', methods=['GET', 'POST'])
@login_required
def finish_order(s_sellerkey, o_orderkey, l_linenumber):
    # Check if the seller has enough quantity
    lineitem_info = Seller.get_lineitem_info(s_sellerkey, o_orderkey, l_linenumber)
    product_key = lineitem_info['product_key']
    inventory = Seller.check_quantity(s_sellerkey, o_orderkey, l_linenumber, product_key)
    if inventory:
        # If there is enough quantity, mark the order line item as fulfilled
        Seller.order_finish(s_sellerkey, o_orderkey, l_linenumber, product_key, inventory)
        flash('Order line item marked as fulfilled.', 'success')
    else:
        flash('The item is out of stock.', 'error')
    return redirect(url_for('sellers.seller_order', s_sellerkey=s_sellerkey))


@bp.route('/seller/<s_sellerkey>/review', methods=['GET'])
@login_required
def seller_review(s_sellerkey):
    seller_review_counts = SellerReview.get_seller_review_counts(s_sellerkey)
    seller_review_rating = SellerReview.get_seller_rating(s_sellerkey)
    seller_reviews = SellerReview.get_seller_reviews(s_sellerkey)
    return render_template('seller_review.html', seller_key=s_sellerkey, seller_reviews=seller_reviews, seller_rating = seller_review_rating, seller_review_counts = seller_review_counts)


@bp.route('/seller/<s_sellerkey>/profile', methods=['GET', 'POST'])
@login_required
def seller_profile(s_sellerkey):
    seller_profile = Seller.get_seller_information(s_sellerkey)
    return render_template('seller_profile.html', seller_key=s_sellerkey, seller_profile=seller_profile)


@bp.route('/categories')
def get_categories():
    categories = Category.get_all()
    return jsonify(categories=[cat.serialize() for cat in categories])


@bp.route('/create_category', methods=['POST'])
def create_category():
    try:
        # Extract category name from the request data
        category_name = request.json.get('category_name')

        # Check if the category name is provided
        if not category_name:
            raise ValueError('Category name is required.')

        # Create the new category
        category_created = Category.create_category(category_name)

        # Check if the category was successfully created
        if category_created:
            return jsonify({'success': True, 'message': 'Category created successfully'})
        else:
            raise ValueError('Failed to create category.')

    except Exception as e:
        # Handle any errors and respond with an error message
        return jsonify({'success': False, 'error': str(e)})
