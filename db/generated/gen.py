import csv
import random
from faker import Faker
from werkzeug.security import generate_password_hash
from datetime import datetime
import itertools

fake = Faker()
Faker.seed(0)

num_users = num_carts = 100 
num_products = 200

num_product_carts = 200

num_sellers = 50 
num_categories = 50
num_lineitems = 5
num_orders = 200
num_product_reviews = 50
num_seller_reviews = 50
num_product_sellers = 500

path_prefix = './db/data/'

def get_csv_writer(filename):
    f = open(path_prefix+filename, 'w', newline='', encoding='utf-8')
    writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, escapechar=None)
    return writer, f

# Helper to close files after writing
def close_file(f):
    f.close()

# Generate Users
def gen_users(num_users):
    valid_user_ids = []
    with open(path_prefix+'Users.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerow(['u_userkey', 'u_email', 'u_firstname', 'u_lastname', 'u_password', 'u_balance', 'u_companyname',
                          'u_streetaddress', 'u_city', 'u_stateregion', 'u_zipcode', 'u_country', 'u_phonenumber', 'u_imageurl'])
        for uid in range(1, num_users + 1):
            valid_user_ids.append(uid)
            u_email = fake.unique.email()
            u_firstname = fake.first_name()
            u_lastname = fake.last_name()
            u_password = generate_password_hash(fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True))
            u_balance = round(random.uniform(0, 10000), 2)
            u_companyname = fake.company() if random.choice([True, False]) else ''
            u_streetaddress = fake.street_address()
            u_city = fake.city()
            u_stateregion = fake.state()
            u_zipcode = fake.zipcode()
            u_country = fake.country()
            u_phonenumber = fake.numerify(text="##########")
            u_imageurl = 'img/user_profile_default.jpg'  # Default image URL
            writer.writerow([uid, u_email, u_firstname, u_lastname, u_password, u_balance, u_companyname, u_streetaddress, 
                             u_city, u_stateregion, u_zipcode, u_country, u_phonenumber,u_imageurl])
    return valid_user_ids


# Generate Categories
def gen_categories(num_categories):
    valid_category_ids = []
    writer, file = get_csv_writer('Categories.csv')
    writer.writerow(['cat_catkey', 'cat_catname'])
    for cid in range(1, num_categories + 1):
        valid_category_ids.append(cid)
        cat_name = fake.word()
        writer.writerow([cid, cat_name])
    close_file(file)
    return valid_category_ids

# Generate Products
def gen_products(num_products, valid_category_ids):
    valid_product_ids = []
    writer, file = get_csv_writer('Products.csv')
    writer.writerow(['p_productkey', 'p_productname', 'p_price', 'p_description', 'p_imageurl', 'p_catkey'])
    for pid in range(1, num_products + 1):
        valid_product_ids.append(pid)
        p_name = fake.word()
        p_price = round(random.uniform(10.0, 500.0), 2)
        p_description = fake.text(max_nb_chars=200)
        p_imageurl = fake.image_url()
        p_catkey = random.choice(valid_category_ids)
        writer.writerow([pid, p_name, p_price, p_description, p_imageurl, p_catkey])
    close_file(file)
    return valid_product_ids

# Generate Sellers
def gen_sellers(num_sellers, valid_user_ids):
    valid_seller_ids = []
    writer, file = get_csv_writer('Sellers.csv')
    writer.writerow(['s_sellerkey', 's_userkey', 's_companyname', 's_registrationdate'])
    for sid in range(1, num_sellers + 1):
        valid_seller_ids.append(sid)
        s_userkey = random.choice(valid_user_ids)
        s_companyname = fake.company()
        s_registrationdate = fake.date_between(start_date='-2y', end_date='today')
        writer.writerow([sid, s_userkey, s_companyname, s_registrationdate])
    close_file(file)
    return valid_seller_ids

# Generate ProductSeller (joint table for products and sellers)
def gen_product_sellers(num_product_sellers, valid_product_ids, valid_seller_ids):
    valid_product_seller_pairs = []
    writer, file = get_csv_writer('ProductSellers.csv')
    writer.writerow(['ps_productkey', 'ps_sellerkey', 'ps_quantity', 'ps_price', 'ps_discount', 'ps_createtime'])
    pairs = set()
    while len(pairs) < num_product_sellers:
        ps_productkey = random.choice(valid_product_ids)
        ps_sellerkey = random.choice(valid_seller_ids)
        if (ps_productkey, ps_sellerkey) not in pairs:
            pairs.add((ps_productkey, ps_sellerkey))
            valid_product_seller_pairs.append((ps_productkey, ps_sellerkey))
            ps_quantity = random.randint(1, 100)
            ps_price = round(random.uniform(10.0, 500.0), 2)
            ps_discount = round(random.uniform(0.0, ps_price), 2)
            ps_createtime = fake.date_between(start_date='-1y', end_date='today')
            writer.writerow([ps_productkey, ps_sellerkey, ps_quantity, ps_price, ps_discount, ps_createtime])
    close_file(file)
    return valid_product_seller_pairs

# Generate Orders
def gen_orders(num_orders, valid_user_ids):
    valid_order_ids = []
    order_dates = {}  # Dictionary to store order keys and their creation dates

    writer, file = get_csv_writer('Orders.csv')
    writer.writerow(['o_orderkey', 'o_userkey', 'o_totalprice', 'o_ordercreatedate', 'o_fulfillmentdate'])
    
    for oid in range(1, num_orders + 1):
        o_userkey = random.choice(valid_user_ids)
        o_totalprice = round(random.uniform(20.0, 2000.0), 2)
        o_ordercreatedate = fake.date_between(start_date='-1y', end_date='today')
        o_ordercreatedate_str = o_ordercreatedate.strftime('%Y-%m-%d')
        
        # Store the order date in the dictionary using order ID as the key
        order_dates[oid] = o_ordercreatedate

        if random.choice([True, False]):
            o_fulfillmentdate = fake.date_between_dates(date_start=o_ordercreatedate, date_end=datetime.now())
            o_fulfillmentdate_str = o_fulfillmentdate.strftime('%Y-%m-%d')
        else:
            o_fulfillmentdate_str = '\\N'  # For CSV compatibility with NULL values

        valid_order_ids.append(oid)
        writer.writerow([oid, o_userkey, o_totalprice, o_ordercreatedate_str, o_fulfillmentdate_str])
    
    close_file(file)
    print("Generated Orders and captured their creation dates.")

    return valid_order_ids, order_dates

def gen_seller_reviews(num_seller_reviews, valid_seller_ids, valid_user_ids):
    writer, file = get_csv_writer('SellerReviews.csv')
    writer.writerow(['sr_sellerkey', 'sr_userkey', 'sr_sellername', 'sr_reviewdate', 'sr_review', 'sr_rating'])
    
    # Generate unique pair combinations of seller IDs and user IDs
    unique_pairs = set(itertools.product(valid_seller_ids, valid_user_ids))
    
    for _ in range(num_seller_reviews):
        if not unique_pairs:
            break  # Stop if there are no more unique pairs to assign
        sr_sellerkey, sr_userkey = unique_pairs.pop()
        sr_sellername = fake.company()
        sr_reviewdate = fake.date_between(start_date='-1y', end_date='today')
        sr_review = fake.text(max_nb_chars=200)
        sr_rating = round(random.uniform(1, 5), 1)
        writer.writerow([sr_sellerkey, sr_userkey, sr_sellername, sr_reviewdate, sr_review, sr_rating])
    
    close_file(file)

def gen_product_reviews(num_product_reviews, valid_product_ids, valid_user_ids):
    writer, file = get_csv_writer('ProductReviews.csv')
    writer.writerow(['pr_productkey', 'pr_userkey', 'pr_productname', 'pr_reviewdate', 'pr_review', 'pr_rating'])
    
    # Generate unique pair combinations of product IDs and user IDs
    unique_pairs = set(itertools.product(valid_product_ids, valid_user_ids))
    
    for _ in range(num_product_reviews):
        if not unique_pairs:
            break  # Stop if there are no more unique pairs to assign
        pr_productkey, pr_userkey = unique_pairs.pop()
        pr_productname = fake.word()
        pr_reviewdate = fake.date_between(start_date='-1y', end_date='today')
        pr_review = fake.text(max_nb_chars=200)
        pr_rating = round(random.uniform(1, 5), 1)
        writer.writerow([pr_productkey, pr_userkey, pr_productname, pr_reviewdate, pr_review, pr_rating])
    
    close_file(file)

def gen_cart(num_carts, valid_user_ids):
    valid_cart_ids = []
    writer, file = get_csv_writer('Carts.csv')
    writer.writerow(['c_cartkey', 'c_userkey'])  # Assuming c_cartkey is auto-generated and should not be included in CSV.
    for i in range(1, num_carts + 1):
            c_userkey = random.choice(valid_user_ids)
            # Add the generated cart ID to the list
            valid_cart_ids.append(i)
            # Write to CSV without the cart ID, as it's auto-generated by the database
            writer.writerow([i, c_userkey])
    close_file(file)
    return valid_cart_ids

def gen_productcart(num_product_carts, valid_cart_ids, valid_product_seller_pairs):
    writer, file = get_csv_writer('ProductCarts.csv')
    writer.writerow(['pc_prodcartkey', 'pc_cartkey', 'pc_productkey', 'pc_sellerkey', 'pc_savequantity', 'pc_incartquantity'])  # Assuming pc_prodcartkey is auto-generated and should not be included in CSV.
    for i in range(1, num_product_carts + 1):
        pc_cartkey = random.choice(valid_cart_ids)
        (pc_productkey, pc_sellerkey) = random.choice(valid_product_seller_pairs)
        pc_savequantity = random.randint(1, 10)  # Assuming some random save quantity
        pc_incartquantity = random.randint(1, 10)  # Assuming some random in-cart quantity
        writer.writerow([i, pc_cartkey, pc_productkey, pc_sellerkey, pc_savequantity, pc_incartquantity])  # None is for the auto-generated pc_prodcartkey
    close_file(file)

def gen_lineitems(num_lineitems, available_oids, available_product_seller_pairs, order_dates):
    writer, file = get_csv_writer('LineItems.csv')
    writer.writerow(['l_linenumber', 'l_orderkey', 'l_productkey', 'l_sellerkey', 'l_quantity', 'l_originalprice', 'l_fulfillmentdate', 'l_discount', 'l_tax'])
    print('Generating line items...', end=' ', flush=True)
    
    for order_key in available_oids:
        for line_item_id in range(1, num_lineitems+1):
            product_key, seller_key = random.choice(available_product_seller_pairs)  # Randomly pick a valid product-seller pair
            quantity = random.randint(1, 10)  # Generate a random quantity between 1 and 10
            original_price = round(random.uniform(5, 200), 2)  # Random original price between $5 and $200
            discount = round(random.uniform(0, original_price * 0.5), 2)  # Discount up to 50% of the original price
            tax = round(original_price * 0.1, 2)  # Tax is assumed to be 10% of the original price

            # Fetch the order date from the dictionary using the order_key
            order_date = order_dates.get(order_key)
            
            # Simulate fulfillment date
            if random.choice([True, False]) and order_date:
                o_fulfillmentdate = fake.date_between_dates(date_start=order_date, date_end=datetime.now())
                o_fulfillmentdate_str = o_fulfillmentdate.strftime('%Y-%m-%d')
            else:
                o_fulfillmentdate_str = '\\N'  # Use '\\N' which PostgreSQL recognizes as NULL

            writer.writerow([line_item_id, order_key, product_key, seller_key, quantity, original_price, o_fulfillmentdate_str, discount, tax])

    close_file(file)
    print('Line item generation completed.')

available_uids = gen_users(num_users)
# print(available_uids)  
available_catids = gen_categories(num_categories)
available_pids = gen_products(num_products, available_catids)
available_sellerids = gen_sellers(num_sellers, available_uids)
available_product_seller_pairs = gen_product_sellers(num_product_sellers, available_pids, available_sellerids)
available_oids, order_dates = gen_orders(num_orders, available_uids)
available_seller_reviews = gen_seller_reviews(num_seller_reviews, available_sellerids, available_uids)
available_product_reviews = gen_product_reviews(num_product_reviews, available_pids, available_uids)
available_cart_ids = gen_cart(num_carts, available_uids)
gen_productcart(num_product_carts, available_cart_ids, available_product_seller_pairs)
gen_lineitems(num_lineitems, available_oids, available_product_seller_pairs, order_dates)

