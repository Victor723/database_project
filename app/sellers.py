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
    # Initialize start_date and end_date with default values
    start_date = datetime(2024, 1, 1).date()
    end_date = datetime(2024, 12, 31).date()
    
    # Check if the request method is POST
    if request.method == 'POST':
        # Get start_date and end_date from the form data
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        # Convert start_date and end_date to datetime.date objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    user_info = Seller.get_seller_information(s_sellerkey)
    total_income = 0
    months = []
    monthly_incomes = []

    # Check if user_info is not empty and contains user's name
    if user_info:
        seller_name = user_info[0]['first_name'] + user_info[0]['last_name']
        total_income = Seller.get_fulfilled_order_total_price(s_sellerkey)
        # Get monthly income data based on the selected period
        monthly_income_data = Seller.get_monthly_income(s_sellerkey, start_date, end_date)
        months = list(monthly_income_data.keys())
        monthly_incomes = list(monthly_income_data.values())

    else:
        seller_name = "User Not Found"
    
    # Render the HTML template with the fetched data
    return render_template('seller_homepage.html', seller_name=seller_name, seller_key=s_sellerkey, 
                           total_income=total_income, months=months, monthly_incomes=monthly_incomes, 
                           start_date=start_date, end_date=end_date)  # Pass start_date and end_date variables to pre-fill the form


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
    return render_template('seller_inventory.html', seller_key=s_sellerkey, productseller_info=productseller_info,
                           current_page=page, total_pages=total_pages, sort_column=sort_column, sort_order=sort_order)


@bp.route('/seller/<s_sellerkey>/<p_productkey>/details', methods=['GET', 'POST'])
@login_required
def seller_product_details(s_sellerkey, p_productkey):
    # Get product information for the specified seller key and product key
    product_info = ProductSeller.get_product_info(s_sellerkey, p_productkey)
    # Render the template with the product information
    return render_template('seller_product_details.html', product_info=product_info, seller_key=s_sellerkey)


@bp.route('/seller/<s_sellerkey>/<p_productkey>/delete', methods=['GET','POST'])
@login_required
def delete_product(s_sellerkey, p_productkey):
    # Attempt to delete the product
    message = ProductSeller.delete_product(s_sellerkey, p_productkey)

    # Check if the product was successfully deleted
    if "successfully" in message:
        # Product was successfully deleted
        return redirect(url_for('sellers.seller_inventory', s_sellerkey=s_sellerkey))
    else:
        # Product deletion failed
        return jsonify({'message': message}), 500


@bp.route('/seller/<s_sellerkey>/<p_productkey>/modify', methods=['GET', 'POST'])
@login_required
def modify_product(s_sellerkey, p_productkey):
    if request.method == 'POST':
        # Retrieve form data
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_description = request.form['product_description']
        product_imageurl = request.form['product_imageurl']
        product_quantity = request.form['product_quantity']
        product_discount = request.form['product_discount']
        current_time = datetime.now()

        # Update Product table
        app.db.execute(
            """
            UPDATE Product
            SET p_productname = :product_name,
                p_price = :product_price,
                p_description = :product_description,
                p_imageurl = :product_imageurl
            WHERE p_productkey = :product_key
            """,
            product_name=product_name,
            product_key=p_productkey,
            product_price=product_price,
            product_description=product_description,
            product_imageurl=product_imageurl
        )

        # Update ProductSeller table if necessary
        app.db.execute(
            """
            UPDATE ProductSeller
            SET ps_price = :product_price,
                ps_quantity = :product_quantity,
                ps_discount = :product_discount,
                ps_createtime = :current_time
            WHERE ps_productkey = :product_key AND ps_sellerkey = :seller_key
            """,
            product_price=product_price,
            product_key=p_productkey,
            seller_key=s_sellerkey,
            product_quantity=product_quantity,
            product_discount=product_discount,
            current_time=current_time
        )

        # Redirect to inventory page after modification
        return redirect(url_for('sellers.seller_inventory', s_sellerkey=s_sellerkey))
    else:
        # Retrieve product information for pre-filling the form
        product_info = ProductSeller.get_product_info(s_sellerkey, p_productkey)
        if product_info:
            return render_template('modify_product.html', seller_key=s_sellerkey, product_key=p_productkey, product_info=product_info)
        else:
            flash('Product not found.', 'error')
            return redirect(url_for('sellers.seller_inventory', s_sellerkey=s_sellerkey))


@bp.route('/seller/<s_sellerkey>/add_product', methods=['GET', 'POST'])
@login_required
def add_product(s_sellerkey):
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        search_results = Product.search_products_by_name(search_query)
        return render_template('search_results.html', seller_key=s_sellerkey, search_results=search_results, search_query=search_query)
    else:
        return render_template('add_product.html', seller_key=s_sellerkey)


@bp.route('/seller/<s_sellerkey>/add_product/create', methods=['GET', 'POST'])
@login_required
def create_product(s_sellerkey):
    if request.method == 'POST':
        # Check if 'Add New Category' was selected
        if request.form['category_key'] == 'new_category':
            # Create new category
            new_category_name = request.form['new_category_name']
            category_key = Category.create_category(new_category_name)
            if not category_key:
                flash('Failed to create new category.', 'error')
                return redirect(url_for('sellers.create_product', s_sellerkey=s_sellerkey))
        else:
            category_key = request.form['category_key']

        # Continue with product creation
        product_key = Product.find_max_productkey() + 1
        product_name = request.form['product_name']
        product_price = request.form['price']
        product_description = request.form['description']
        product_image_url = request.form['imageurl']
        quantity = request.form['quantity']
        discount = request.form['discount']
        try:
            Product.create_product(product_key, product_name, product_price, product_description, product_image_url, category_key)
            ProductSeller.create_productseller(product_key, s_sellerkey, quantity, discount, product_price)
            flash('Product created successfully.', 'success')
            return redirect(url_for('sellers.add_product', s_sellerkey=s_sellerkey))
        except Exception as e:
            flash(str(e), 'error')
            return redirect(url_for('sellers.create_product', s_sellerkey=s_sellerkey))
    else:
        categories = Category.get_all()
        return render_template('create_product.html', seller_key=s_sellerkey, categories=categories)


@bp.route('/seller/<s_sellerkey>/add_product/<p_productkey>', methods=['GET', 'POST'])
@login_required
def add_exit_product(s_sellerkey, p_productkey):
    if request.method == 'POST':
        # Retrieve form data
        product_price = request.form['product_price']
        product_quantity = request.form['product_quantity']
        product_discount = request.form['product_discount']
        current_time = datetime.now()

        # Check if the product already exists for this seller
        existing_product = ProductSeller.get_product_info(s_sellerkey, p_productkey)
        if existing_product:
            flash("You have already added this product.", 'error')
            return redirect(url_for('sellers.add_product', s_sellerkey=s_sellerkey))
        else:
           # Insert product seller information into the ProductSeller table
            app.db.execute(
                """
                INSERT INTO ProductSeller (ps_productkey, ps_sellerkey, ps_quantity, ps_price, ps_discount, ps_createtime)
                VALUES (:product_key, :seller_key, :quantity, :price, :discount, :createtime)
                """,
                product_key=p_productkey,
                seller_key=s_sellerkey,
                quantity=product_quantity,
                price=product_price,
                discount=product_discount,
                createtime=current_time
            )

            flash("Product added successfully.", 'success')
            return redirect(url_for('sellers.seller_inventory', s_sellerkey=s_sellerkey))
    else:
        # Render the template for adding product information
        product_info = Product.get_prod_details(p_productkey)
        return render_template('add_exit_product.html', seller_key=s_sellerkey, product_info=product_info)
        

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
    try:
        Seller.order_finish(s_sellerkey, o_orderkey, l_linenumber)
        flash('Order line item marked as fulfilled.', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
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

        # Check if the category name already exists
        check_category = Category.check_category(category_name)
        if check_category:
            print("here")
            raise ValueError('Category name already exists.')

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
