from flask import render_template, request
from flask_login import current_user
import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.category import Category

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    # get all available products for sale:
    products = Product.get_all(True)
    categories = Category.get_all()
    # find the products current user has bought:
    
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    
    selected_catkey = request.args.get('category')
    if selected_catkey:
        # Filter products by selected category
        products = Product.get_all_by_category(selected_catkey)
    else:
        # If no category is selected, display all products
        products = Product.get_all()

    if request.method == 'POST':
        if 'topK' in request.form:  
            topK_value = request.form.get('topK')
            if topK_value.isdigit() and int(topK_value) > 0:  
                products = Product.get_top_K(int(topK_value))
            else: 
                products = Product.get_all_sort_by_price()
        # elif request.form.get('action') == 'showAll': 
        #     products = Product.get_all() 

    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           categories=categories,
                           purchase_history=purchases)