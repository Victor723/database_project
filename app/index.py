from flask import render_template, request, url_for, current_app
from flask_paginate import Pagination, get_page_parameter
from flask_login import current_user
from sqlalchemy import or_

from .models.product import Product
from .models.category import Category
from .models.productreview import ProductReview

import logging
logging.basicConfig(level=logging.DEBUG)

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 15

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
    search_term = request.args.get('search', '')
    if search_term:
        products = Product.get_all_by_keyword(search_term)
        
    # Sort products by price decreasingly (and show top K items)
    topK_value = request.args.get('topK', '')
    if topK_value and topK_value.isdigit() and int(topK_value) > 0:  
        products = Product.get_top_K(int(topK_value))

    for product in products:
        product.p_rating = ProductReview.get_product_rating(product.p_productkey)

    curr_page_products = products[(page-1) * per_page : page * per_page]
    total_pages = (len(products) + per_page - 1) // per_page

    return render_template('index.html',
                           avail_products=curr_page_products,
                           categories=categories,
                           search_query=search_term,
                           topK_query=topK_value,
                           total_pages=total_pages)
