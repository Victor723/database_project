from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):

    # def __init__(self, userkey, email, firstname, lastname, password, balance, companyname, streetaddress, city, stateregion, zipcode, country, phonenumber):
    #     self.userkey = userkey
    #     self.email = email
    #     self.firstname = firstname
    #     self.lastname = lastname
    #     self.password = password
    #     self.balance = balance
    #     self.companyname = companyname
    #     self.streetaddress = streetaddress
    #     self.city = city
    #     self.stateregion = stateregion
    #     self.zipcode = zipcode
    #     self.country = country
    #     self.phonenumber = phonenumber

    def __init__(self, userkey, email, firstname, lastname):
        self.userkey = userkey
        self.email = email
        self.firstname = firstname
        self.lastname = lastname

    def get_id(self):
        return str(self.userkey)
    
    def get_balance(self):
        return self.balance
    
    @staticmethod
    def get_balance(userkey):
        rows = app.db.execute("""
            SELECT u_balance
            FROM Users
            WHERE u_userkey = :userkey
            """,
            userkey=userkey)
        return rows
    

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
            SELECT u_password, u_userkey, u_email, u_firstname, u_lastname
            FROM Users
            WHERE u_email = :email
            """,
            email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
            SELECT u_email
            FROM Users
            WHERE u_email = :email
            """,
            email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname):
        try:
            rows = app.db.execute("""
                INSERT INTO Users(u_email, u_password, u_firstname, u_lastname)
                VALUES(:email, :password, :firstname, :lastname)
                RETURNING u_userkey
                """,
                email=email,
                password=generate_password_hash(password),
                firstname=firstname, lastname=lastname)
            userkey = rows[0][0]
            return User.get(userkey)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(userkey):
        rows = app.db.execute("""
            SELECT u_userkey, u_email, u_firstname, u_lastname
            FROM Users
            WHERE u_userkey = :userkey
            """,
            userkey=userkey)
        return User(*(rows[0])) if rows else None
    




    

    @staticmethod
    def get_order_history_by_id(userkey):
        rows = app.db.execute("""
            SELECT
                O.o_orderkey AS Order_Key,
                O.o_ordercreatedate AS Order_Date,
                P.p_productkey AS Product_Key,
                P.p_productname AS Product_Name,
                L.l_quantity AS Quantity,
                L.l_originalprice AS Original_Price
            FROM
                Orders O
            JOIN Lineitem L ON O.o_orderkey = L.l_orderkey
            JOIN Product P ON L.l_productkey = P.p_productkey
            WHERE
                O.o_userkey = :userkey
            ORDER BY O.o_ordercreatedate;
            """,
            userkey=userkey)
        # rows: list of tuples
        return rows
