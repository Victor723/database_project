from werkzeug.security import generate_password_hash
import csv
from faker import Faker

num_users = 100
num_products = 2000
num_purchases = 2500

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix')


# def gen_users(num_users):
#     with open('Users.csv', 'w') as f:
#         writer = get_csv_writer(f)
#         print('Users...', end=' ', flush=True)
#         for uid in range(num_users):
#             if uid % 10 == 0:
#                 print(f'{uid}', end=' ', flush=True)
#             profile = fake.profile()
#             email = profile['mail']
#             plain_password = f'pass{uid}'
#             password = generate_password_hash(plain_password)
#             name_components = profile['name'].split(' ')
#             firstname = name_components[0]
#             lastname = name_components[-1]
#             writer.writerow([uid, email, password, firstname, lastname])
#         print(f'{num_users} generated')
#     return

def gen_users(num_users):
    with open('./db/generated/Users.csv', 'w') as f:
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
            balance = round(fake.pydecimal(left_digits=4, right_digits=2, positive=True), 2)
            companyname = fake.company()
            streetaddress = fake.street_address()
            city = fake.city()
            stateregion = fake.state()
            zipcode = fake.zipcode()
            country = fake.country()
            phonenumber = fake.phone_number()
            writer.writerow([email, password, firstname, lastname, balance, companyname, streetaddress, city, stateregion, zipcode, country, phonenumber])
        print(f'{num_users} generated')



def gen_products(num_products):
    available_pids = []
    with open('./db/generated/Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            description = fake.text(max_nb_chars=200)
            imageurl = fake.image_url()
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            # price = round(fake.pydecimal(left_digits=3, right_digits=2, positive=True), 2)
            catkey = fake.random_int(min=1, max=5)  # Assuming 5 categories exist
            link = fake.url()

            available = fake.random_element(elements=('true', 'false'))
            if available == 'true':
                available_pids.append(pid)
            # writer.writerow([pid, name, price, available])
            writer.writerow([name, description, imageurl, price, catkey, link])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids


def gen_purchases(num_purchases, available_pids):
    with open('./db/generated/Purchases.csv', 'w') as f:
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
    return


gen_users(num_users)
available_pids = gen_products(num_products)
gen_purchases(num_purchases, available_pids)
