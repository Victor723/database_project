from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):

    def __init__(self, userkey, email, firstname, lastname, balance, companyname, 
                 streetaddress, city, stateregion, zipcode, country, phonenumber,
                 imageurl):
        self.userkey = userkey
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.balance = balance
        self.companyname = companyname
        self.streetaddress = streetaddress
        self.city = city
        self.stateregion = stateregion
        self.zipcode = zipcode
        self.country = country
        self.phonenumber = phonenumber
        self.imageurl = imageurl


    def get_id(self):
        return str(self.userkey)

    @staticmethod
    def get_balance(userkey):
        try:
            rows = app.db.execute("""
                SELECT u_balance
                FROM Users
                WHERE u_userkey = :userkey
                """,
                userkey=userkey)
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
        # elif not check_password_hash(rows[0][0], password):  # incorrect password
        #     app.logger.info('Invalid login credentials.')
        #     return None
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
    def register(email, password, firstname, lastname, companyname, streetaddress, city, stateregion, zipcode, country, phonenumber):
        if not (email and password and firstname and lastname):
            return {'error': 'Missing required fields'}
        try:
            rows = app.db.execute("""
                INSERT INTO Users(u_email, u_password, u_firstname, u_lastname,
                    u_companyname, u_streetaddress, u_city, 
                    u_stateregion, u_zipcode, u_country, u_phonenumber)
                VALUES(:email, :password, :firstname, :lastname,
                    :companyname, :streetaddress, :city, 
                    :stateregion, :zipcode, :country, :phonenumber)
                RETURNING u_userkey
                    """,
                email=email,
                password=generate_password_hash(password),
                firstname=firstname, 
                lastname=lastname,
                companyname=companyname,
                streetaddress=streetaddress,
                city=city,
                stateregion=stateregion,
                zipcode=zipcode,
                country=country,
                phonenumber=phonenumber)
            userkey = rows[0][0]
            return User.get(userkey)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            app.logger.error(f"Unexpected error during registration: {e}")
            return None

    
    @staticmethod
    @login.user_loader
    def get(userkey):
        try:
            rows = app.db.execute("""
                SELECT u_userkey, u_email, u_firstname, u_lastname, u_balance, u_companyname, 
                    u_streetaddress, u_city, u_stateregion, u_zipcode, u_country, u_phonenumber,
                    u_imageurl
                FROM Users
                WHERE u_userkey = :userkey
                """,
                userkey=userkey)
            return User(*(rows[0])) if rows else None
        except Exception as e:
            app.logger.error(f"Failed to retrieve user {userkey}: {str(e)}")
            return None
    
    @staticmethod
    def update_user_details(userkey, email=None, firstname=None, lastname=None):
        updates = {}
        if email:
            updates['u_email'] = email
        if firstname:
            updates['u_firstname'] = firstname
        if lastname:
            updates['u_lastname'] = lastname
            
        if updates:
            query = """UPDATE Users SET """
            query += ', '.join(f"{k} = :{k}" for k in updates.keys())
            query += """ WHERE u_userkey = :userkey RETURNING u_userkey """

        params = updates
        params['userkey'] = userkey
        try:
            rows = app.db.execute(query, **params)
            return rows[0][0] == userkey  # True if the update was successful
        except Exception as e:
            app.logger.error(f"Failed to update user info for {userkey}: {str(e)}")
            return False
        

    @staticmethod
    def check_password(userkey, old_plain_password): # check pwd given a userkey, for password update
        try:
            rows = app.db.execute("""
                SELECT u_password
                FROM Users
                WHERE u_userkey = :userkey
                """, 
                userkey=userkey)
            
            if not rows:
                app.logger.error(f"User not found or no password set for user")
                return False
            
            password_hash = rows[0][0]
            return check_password_hash(password_hash, old_plain_password)
        except Exception as e:
            app.logger.error(f"An error occurred: {e}")
            return False
        

    @staticmethod
    def update_password(userkey, new_plain_password):
        try:
            rows = app.db.execute("""
                UPDATE Users
                SET u_password = :new_password_hash
                WHERE u_userkey = :userkey
                RETURNING u_userkey
                """,
                userkey=userkey,
                new_password_hash=generate_password_hash(new_plain_password))
            
            return rows and rows[0][0] == userkey
        except Exception as e:
            app.logger.error(f"An error occurred: {e}")
            return False


    @staticmethod
    def update_address(userkey, companyname=None, streetaddress=None, country=None, stateregion=None, 
                       city=None, zipcode=None, phonenumber=None):
        updates = {}
        if companyname:
            updates['u_companyname'] = companyname
        if streetaddress:
            updates['u_streetaddress'] = streetaddress
        if country:
            updates['u_country'] = country
        if stateregion:
            updates['u_stateregion'] = stateregion
        if city:
            updates['u_city'] = city
        if zipcode:
            updates['u_zipcode'] = zipcode
        if phonenumber:
            updates['u_phonenumber'] = phonenumber

        if updates:
            query = """UPDATE Users SET """
            query += ', '.join(f"{k} = :{k}" for k in updates.keys())
            query += """ WHERE u_userkey = :userkey RETURNING u_userkey """

        params = updates
        params['userkey'] = userkey

        try:
            rows = app.db.execute(query, **params)
            app.logger.info(f"updated address for {userkey}") 
            return rows[0][0] == userkey  # True if the update was successful
        except Exception as e:
            app.logger.error(f"An error occurred: {e}") 
            return False
        
    
    @staticmethod
    def update_balance(userkey, amount, newbalance):
        try:
            rows = app.db.execute("""
                UPDATE Users
                SET u_balance = u_balance + :amount
                WHERE u_userkey = :userkey
                RETURNING u_userkey, u_balance
                """,
                userkey=userkey,
                amount=amount)
            app.logger.info(f"updated balance by {amount} to {newbalance}") 
            return rows[0][0] == userkey and rows[0][1] == newbalance # true if userkey match and u_balance = new balance
        except Exception as e:
            app.logger.error(f"An error occurred: {e}") 
            return False
        
    
    @staticmethod
    def update_imageurl(userkey, newurl):
        try:
            rows = app.db.execute("""
                UPDATE Users
                SET u_imageurl = :newurl
                WHERE u_userkey = :userkey
                RETURNING u_userkey
                """,
                userkey=userkey,
                newurl=newurl)
            app.logger.info(f"updated image url for user {userkey}") 
            return rows[0][0] == userkey
        except Exception as e:
            app.logger.error(f"An error occurred: {e}") 
            return False
        
    
    @staticmethod
    def get_monthly_expenditure(userkey):
        try:
            rows = app.db.execute("""
                SELECT
                    EXTRACT(YEAR FROM o_ordercreatedate) AS order_year,
                    EXTRACT(MONTH FROM o_ordercreatedate) AS order_month,
                    SUM(o_totalprice) AS total_spent
                FROM Orders
                WHERE
                    o_userkey = :userkey AND
                    o_ordercreatedate >= CURRENT_DATE - INTERVAL '1 year'
                GROUP BY
                    EXTRACT(YEAR FROM o_ordercreatedate),
                    EXTRACT(MONTH FROM o_ordercreatedate)
                ORDER BY
                    order_year,
                    order_month;
                """,
                userkey=userkey)
            # app.logger.info(f"get_monthly_expenditure for {userkey}") 
            # app.logger.info(f"monthly_expenditure: {rows}") 
            return rows if rows else None
        except Exception as e:
            app.logger.error(f"Failed to fetch monthly expenditure for user {userkey}: {str(e)}")
            return None
        
    @staticmethod
    def get_weekly_expenditure(userkey):
        try:
            rows = app.db.execute("""
                SELECT
                    EXTRACT(YEAR FROM o_ordercreatedate) AS order_year,
                    EXTRACT(WEEK FROM o_ordercreatedate) AS order_week,
                    SUM(o_totalprice) AS total_spent
                FROM Orders
                WHERE
                    o_userkey = :userkey AND
                    o_ordercreatedate >= CURRENT_DATE - INTERVAL '1 year'
                GROUP BY
                    EXTRACT(YEAR FROM o_ordercreatedate),
                    EXTRACT(WEEK FROM o_ordercreatedate)
                ORDER BY
                    order_year,
                    order_week;
                """,
                userkey=userkey)
            # app.logger.info(f"get_weekly_expenditure for {userkey}") 
            return rows if rows else None
        except Exception as e:
            app.logger.error(f"Failed to fetch weekly expenditure for user {userkey}: {str(e)}")
            return None
        
    @staticmethod
    def get_user_spending_summary(userkey, startdate, enddate):
        try:
            rows = app.db.execute("""
                SELECT 
                    c.cat_catname AS Category_Name,
                    CAST(SUM((l.l_originalprice - COALESCE(l.l_discount, 0) + COALESCE(l.l_tax, 0)) * l.l_quantity) AS DECIMAL(10,2)) AS Total_Spending_Per_Category
                FROM 
                    Orders o
                JOIN 
                    Lineitem l ON o.o_orderkey = l.l_orderkey
                JOIN 
                    Product p ON l.l_productkey = p.p_productkey
                JOIN 
                    Category c ON p.p_catkey = c.cat_catkey
                WHERE 
                    o.o_userkey = :userkey
                    AND o.o_ordercreatedate BETWEEN :startdate AND :enddate
                GROUP BY 
                    c.cat_catname
                UNION ALL
                SELECT 
                    'Total' AS Category_Name,
                    CAST(SUM(o.o_totalprice) AS DECIMAL(10,2)) AS Total_Spending
                FROM 
                    Orders o
                WHERE 
                    o.o_userkey = :userkey
                    AND o.o_ordercreatedate BETWEEN :startdate AND :enddate;
                """,
                userkey=userkey,
                startdate=startdate,
                enddate=enddate)
            app.logger.info(f"get_user_spending_summary for {userkey}") 
            # app.logger.info(f"{rows}") 
            return rows if rows else None
        except Exception as e:
            app.logger.error(f"Failed to fetch spending_summary for user {userkey}: {str(e)}")
            return None

    @staticmethod
    def get_order_counts(userkey):
        try:
            rows = app.db.execute("""
                SELECT 
                    o_userkey,
                    COUNT(*) AS total_orders,
                    COUNT(o_fulfillmentdate) AS completed_orders,
                    COUNT(*) - COUNT(o_fulfillmentdate) AS in_progress_orders
                FROM 
                    Orders
                WHERE 
                    o_userkey = :userkey
                GROUP BY 
                    o_userkey;
                """,
                userkey=userkey)
            # app.logger.info(f"{rows}") 
            if rows and rows[0][0] == userkey:
                return rows[0][1:] 
            else:
                return None
        except Exception as e:
            app.logger.error(f"Failed to fetch order counts for user {userkey}: {str(e)}")
            return None