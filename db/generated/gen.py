from werkzeug.security import generate_password_hash
import csv
from faker import Faker

num_users = 100
num_products = 2000
num_purchases = 2500
num_product_reviews = 500
num_seller_reviews = 500

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


def gen_users(num_users):
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            writer.writerow([uid, email, password, firstname, lastname])
        print(f'{num_users} generated')
    return


def gen_products(num_products):
    available_pids = []
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            available = fake.random_element(elements=('true', 'false'))
            if available == 'true':
                available_pids.append(pid)
            writer.writerow([pid, name, price, available])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids


"""def gen_purchases(num_purchases, available_pids):
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            pid = fake.random_element(elements=available_pids)
            time_purchased = fake.date_time()
            writer.writerow([id, uid, pid, time_purchased])
        print(f'{num_purchases} generated')
    return"""

def gen_product_reviews(num_product_reviews):
    with open('Product_Reviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Product_Reviews...', end=' ', flush=True)
        for pr_productkey in range(num_products):
            if pr_productkey % 10 == 0:
                print(f'{pr_productkey}', end=' ', flush=True)
            pr_userkey = f'{fake.random_int(max=500)}'
            pr_productname = fake.sentence(nb_words=4)[:-1]
            pr_orderkey = f'{str(fake.random_int(max=5000))}'
            pr_reviewdate = fake.date_time()
            pr_review = fake.sentence(nb_words=15)[:-1]
            pr_rating = f'{str(fake.random_int(max=4))}.{fake.random_int(max=9):01}'
            writer.writerow([pr_productkey, pr_userkey, pr_productname, pr_orderkey, pr_reviewdate, pr_review, pr_rating])
        print(f'{num_product_reviews} generated')
    return

def gen_seller_reviews(num_seller_reviews):
    with open('Seller_Reviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller_Reviews...', end=' ', flush=True)
        for sid in range(num_users):
            if sid % 10 == 0:
                print(f'{sid}', end=' ', flush=True)
            uid = f'{fake.random_int(max=500)}'
            seller_name = fake.sentence(nb_words=4)[:-1]
            order_key = f'{str(fake.random_int(max=5000))}'
            time_reviewed = fake.date_time()
            review = fake.sentence(nb_words=15)[:-1]
            rating = f'{str(fake.random_int(max=4))}.{fake.random_int(max=9):01}'
            writer.writerow([sid, uid, seller_name, order_key, time_reviewed, review, rating])
        print(f'{num_product_reviews} generated')
    return

gen_users(num_users)
available_pids = gen_products(num_products)
"""gen_purchases(num_purchases, available_pids)"""
gen_product_reviews(num_product_reviews)
gen_seller_reviews(num_seller_reviews)