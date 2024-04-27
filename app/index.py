from flask import render_template, request
from flask_paginate import Pagination, get_page_parameter
from flask_login import current_user
from sqlalchemy import or_

from .models.product import Product
from .models.purchase import Purchase
from .models.category import Category

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    # get all available products for sale:
    products = Product.get_all()
    categories = Category.get_all()

    # Filter by Categories
    selected_catkey = request.args.get('category')
    if selected_catkey:
        # Filter products by selected category
        products = Product.get_all_by_category(selected_catkey)
    else:
        # If no category is selected, display all products
        products = Product.get_all()

    # Search by Keywords
    search_term = request.args.get('search')
    if search_term:
        #query = Product.query
        #search = "%{}%".format(search_term)
        #query = query.filter(or_(Product.p_productname.ilike(search), Product.p_description.ilike(search)))
        #products = query.all()
        products = Product.get_all_by_keyword(search_term)
        
    # Sort products by price decreasingly (and show top K items)
    if request.method == 'POST':
        if 'topK' in request.form:  
            topK_value = request.form.get('topK')
            if topK_value.isdigit() and int(topK_value) > 0:  
                products = Product.get_top_K(int(topK_value))
            else:  # sort all products if k is not entered
                products = Product.get_all_sort_by_price()


    return render_template('index.html',
                           avail_products=products,
                           categories=categories)