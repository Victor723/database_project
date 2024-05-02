from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):

    def __init__(self, user_key, email, first_name, last_name, balance, company_name, 
             street_address, city, state_region, zip_code, country, phone_number,
             image_url):
        self.user_key = user_key
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.balance = balance
        self.company_name = company_name
        self.street_address = street_address
        self.city = city
        self.state_region = state_region
        self.zip_code = zip_code
        self.country = country
        self.phone_number = phone_number
        self.image_url = image_url

    def get_id(self):
        return str(self.user_key)

    @staticmethod
    def get_balance(user_key):
        try:
            rows = app.db.execute("""
                SELECT ROUND(u_balance, 2)
                FROM Users
                WHERE u_userkey = :user_key
                """,
                user_key=user_key)
            return rows[0][0]
        except Exception as e:
            app.logger.error(f"Unexpected error getting balance: {e}")
            return None
    
    @staticmethod
    def get_by_auth(email, password):
        try:
            rows = app.db.execute("""
                SELECT u_password, u_userkey, u_email, u_firstname, u_lastname, u_balance, u_companyname, 
                    u_streetaddress, u_city, u_stateregion, u_zipcode, u_country, u_phonenumber, u_imageurl
                FROM Users
                WHERE u_email = :email
                """,
                email=email)
        except Exception as e:
            app.logger.error(f"Database error during login for email {email}: {str(e)}")
            return None

        if not rows:  # email not found
            app.logger.info('Invalid login credentials.')
            return None
        elif not check_password_hash(rows[0][0], password):  # incorrect password
            app.logger.info('Invalid login credentials.')
            return None
        else:  # return a newly instantiated user instance
            # Since the password is the first element and not needed in the User constructor,
            # we skip the first element (password) and unpack the rest
            return User(*(rows[0][1:]))
    


    @staticmethod
    def email_exists(email):
        try:
            rows = app.db.execute("""
                SELECT EXISTS(SELECT 1 FROM Users WHERE u_email = :email)
                """,
                email=email)
            return rows[0][0] # true/false
        except Exception as e:
            app.logger.error(f"Error checking if email exists: {e}")
            return False

    @staticmethod
    def register(email, password, first_name, last_name, company_name=None, street_address=None, 
                 city=None, state_region=None, zip_code=None, country=None, phone_number=None):
        if not (email and password and first_name and last_name):
            return {'error': 'Missing required fields'}
        try:
            rows = app.db.execute("""
                INSERT INTO Users(u_email, u_password, u_firstname, u_lastname, u_companyname, 
                                  u_streetaddress, u_city, u_stateregion, u_zipcode, u_country, 
                                  u_phonenumber)
                VALUES(:email, :password, :firstname, :lastname, :companyname, :streetaddress, 
                                  :city, :stateregion, :zipcode, :country, :phonenumber)
                RETURNING u_userkey
                """,
                email=email,
                password=generate_password_hash(password),
                firstname=first_name, 
                lastname=last_name,
                companyname=company_name,
                streetaddress=street_address,
                city=city,
                stateregion=state_region,
                zipcode=zip_code,
                country=country,
                phonenumber=phone_number)
            user_key = rows[0][0]
            return User.get(user_key)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            app.logger.error(f"Unexpected error during registration: {e}")
            return None
        
    @staticmethod
    @login.user_loader
    def get(user_key):
        try:
            rows = app.db.execute("""
                SELECT u_userkey, u_email, u_firstname, u_lastname, u_balance, u_companyname, 
                    u_streetaddress, u_city, u_stateregion, u_zipcode, u_country, u_phonenumber,
                    u_imageurl
                FROM Users
                WHERE u_userkey = :userkey
                """,
                userkey=user_key)
            return User(*(rows[0])) if rows else None
        except Exception as e:
            app.logger.error(f"Failed to retrieve user {user_key}: {str(e)}")
            return None

    @staticmethod
    def get_for_public_view(user_key, is_seller):
        try:
            rows = app.db.execute("""
                SELECT u_firstname, u_lastname, u_imageurl, u_email, u_companyname, u_streetaddress, 
                                  u_city, u_stateregion, u_zipcode, u_country
                FROM Users
                WHERE u_userkey = :userkey
                """,
                userkey=user_key)
            if rows:
                if not is_seller:
                    keys = ['first_name', 'last_name', 'image_url']
                else:
                    keys = ['first_name', 'last_name', 'image_url', 'email', 'company_name', 
                            'street_address', 'city', 'state_region', 'zip_code', 'country']
                return {keys[i]: rows[0][i] for i in range(len(keys))}
            return {}
        except Exception as e:
            app.logger.error(f"Failed to retrieve user {user_key}: {str(e)}")
            return None

    @staticmethod
    def update_user_details(user_key, email=None, first_name=None, last_name=None):
        updates = {}
        if email:
            updates['u_email'] = email
        if first_name:
            updates['u_firstname'] = first_name
        if last_name:
            updates['u_lastname'] = last_name
            
        if updates:
            query = "UPDATE Users SET "
            query += ', '.join(f"{k} = :{k}" for k in updates.keys())
            query += " WHERE u_userkey = :userkey RETURNING u_userkey"

        params = updates
        params['userkey'] = user_key
        try:
            rows = app.db.execute(query, **params)
            return rows[0][0] == user_key  # True if the update was successful
        except Exception as e:
            app.logger.error(f"Failed to update user info for {user_key}: {str(e)}")
            return False
        
    @staticmethod
    def check_password(user_key, old_plain_password):  # check pwd given a userkey, for password update
        try:
            rows = app.db.execute("""
                SELECT u_password
                FROM Users
                WHERE u_userkey = :userkey
                """, 
                userkey=user_key)
            
            if not rows:
                app.logger.error(f"User not found or no password set for user")
                return False
            
            password_hash = rows[0][0]
            return check_password_hash(password_hash, old_plain_password)
        except Exception as e:
            app.logger.error(f"An error occurred: {e}")
            return False

    @staticmethod
    def update_password(user_key, new_plain_password):
        try:
            rows = app.db.execute("""
                UPDATE Users
                SET u_password = :new_password_hash
                WHERE u_userkey = :userkey
                RETURNING u_userkey
                """,
                userkey=user_key,
                new_password_hash=generate_password_hash(new_plain_password))
            
            return rows and rows[0][0] == user_key
        except Exception as e:
            app.logger.error(f"An error occurred: {e}")
            return False

    @staticmethod
    def update_address(user_key, company_name=None, street_address=None, country=None, state_region=None, 
                    city=None, zip_code=None, phone_number=None):
        updates = {}
        if company_name:
            updates['u_companyname'] = company_name
        if street_address:
            updates['u_streetaddress'] = street_address
        if country:
            updates['u_country'] = country
        if state_region:
            updates['u_stateregion'] = state_region
        if city:
            updates['u_city'] = city
        if zip_code:
            updates['u_zipcode'] = zip_code
        if phone_number:
            updates['u_phonenumber'] = phone_number

        if updates:
            query = "UPDATE Users SET "
            query += ', '.join(f"{k} = :{k}" for k in updates.keys())
            query += " WHERE u_userkey = :userkey RETURNING u_userkey"

        params = updates
        params['userkey'] = user_key

        try:
            rows = app.db.execute(query, **params)
            app.logger.info(f"updated address for {user_key}") 
            return rows[0][0] == user_key  # True if the update was successful
        except Exception as e:
            app.logger.error(f"An error occurred: {e}") 
            return False
    
    @staticmethod
    def update_balance(user_key, amount):
        try:
            rows = app.db.execute("""
                UPDATE Users
                SET u_balance = ROUND(u_balance + :amount, 2)
                WHERE u_userkey = :userkey
                RETURNING u_userkey
                """,
                userkey=user_key,
                amount=amount)
            app.logger.info(f"updated balance by {amount}") 
            return rows[0][0] == user_key
        except Exception as e:
            app.logger.error(f"An error occurred: {e}") 
            return False
    
    @staticmethod
    def update_image_url(user_key, new_url):
        try:
            rows = app.db.execute("""
                UPDATE Users
                SET u_imageurl = :newurl
                WHERE u_userkey = :userkey
                RETURNING u_userkey
                """,
                userkey=user_key,
                newurl=new_url)
            app.logger.info(f"updated image url for user {user_key}") 
            return rows[0][0] == user_key
        except Exception as e:
            app.logger.error(f"An error occurred: {e}") 
            return False
            return False
