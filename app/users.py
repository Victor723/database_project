from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
import requests, os, uuid
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Optional
from datetime import date
from decimal import Decimal

from .models.user import User
from .models.seller import Seller
from.models.order import Order

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)



class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    companyname = StringField('Company Name')
    streetaddress = StringField('Street Address')
    city = StringField('City')
    stateregion = StringField('State / Region')
    zipcode = StringField('Zipcode')
    country = StringField('Country')
    phonenumber = StringField('Phone Number', validators=[
        Optional(),
        Regexp(regex=r'^(?:\+?1\s*(?:[.-]\s*)?)?(?:(\(\s*\d{3}\s*\))|\d{3})\s*(?:[.-]\s*)?\d{3}\s*(?:[.-]\s*)?\d{4}$',
            message='Invalid phone number. Format must be XXX-XXX-XXXX or +1 XXX-XXX-XXXX.')
    ])
    submit_user = SubmitField('Sign up')
    submit_seller = SubmitField('Sign up as a seller')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')
        
    def validate_companyname(self, field):
        if 'submit_seller' in request.form and (not field.data or not field.data.strip()):
            raise ValidationError('Company name is required for sellers.')


def get_country_choices():
    url = "https://restcountries.com/v3.1/all"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        countries = response.json()
        # Extract country names and codes; you can adjust the fields as needed
        country_choices = [(country['cca2'], country['name']['common']) for country in countries if 'cca2' in country and 'name' in country]
        return [("","")] + sorted(country_choices, key=lambda choice: choice[1])
    except requests.RequestException as e:
        print(f"Error fetching countries: {e}")
        return []  # Return an empty list in case of error
    


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    # Set country choices dynamically from the REST Countries API
    form.country.choices = get_country_choices()

    if form.validate_on_submit():
        account_type = 'seller' if form.submit_seller.data else 'user'
        user = User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.companyname.data,
                         form.streetaddress.data,
                         form.city.data,
                         form.stateregion.data,
                         form.zipcode.data,
                         form.country.data,
                         form.phonenumber.data)
        if user: 
            if account_type == 'seller':
                registration_date = date.today()
                # if Seller.register(user.userkey, user.companyname, registration_date):
                if True: # use true since Seller.register(user.userkey, user.companyname, registration_date) is not yet implemented
                    flash('Congratulations, you are now registered!')
                else:
                    return render_template('register.html', title='Register', form=form)
            else:
                flash('Congratulations, you are now registered!')

            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)



@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))



class UserDetailsForm(FlaskForm):
    firstname = StringField('First Name', validators=[])
    lastname = StringField('Last Name', validators=[])
    email = StringField('Email', validators=[Email(), Optional()])
    submit_details = SubmitField('Save Changes')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit_password = SubmitField('Save Password')



@bp.route('/user_details', methods=['GET', 'POST'])
@login_required
def user_details():
    user_details_form = UserDetailsForm()
    password_form = ChangePasswordForm()
    if request.method == 'POST':
        if 'submit_details' in request.form:
            if (user_details_form.email.data or user_details_form.firstname.data or user_details_form.lastname.data):
                if user_details_form.validate_on_submit():
                    try:
                        User.update_user_details(
                            current_user.userkey,
                            user_details_form.email.data,
                            user_details_form.firstname.data,
                            user_details_form.lastname.data
                        )
                        # flash('Your account details have been updated.', 'success')
                    except Exception as e:
                        flash(str(e), 'error')
                    return redirect(url_for('users.user_details'))
            
        if 'submit_password' in request.form and password_form.validate_on_submit():
            try:
                if User.check_password(current_user.userkey, password_form.current_password.data):
                    User.update_password(current_user.userkey, password_form.new_password.data)
                    flash('Your password has been changed.', 'success')
                else:
                    flash('Current password is incorrect.', 'error')
            except Exception as e:
                flash(str(e), 'error')
            return redirect(url_for('users.user_details'))

    return render_template('user_details.html', user_details_form=user_details_form, password_form=password_form)


@bp.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    return render_template('user_profile.html',current_user=current_user)



class ChangeAddressForm(FlaskForm):
    companyname = StringField('Company Name')
    streetaddress = StringField('Street Address')
    country = StringField('Country')
    stateregion = StringField('Region / State')
    city = StringField('City')
    zipcode = StringField('Zip Code')
    phonenumber = StringField('Phone Number', validators=[
        Optional(),
        Regexp(regex=r'^(?:\+?1\s*(?:[.-]\s*)?)?(?:(\(\s*\d{3}\s*\))|\d{3})\s*(?:[.-]\s*)?\d{3}\s*(?:[.-]\s*)?\d{4}$',
            message='Invalid phone number; Format must be XXX-XXX-XXXX or +1 XXX-XXX-XXXX; "-" is optional')
        ])
    submit = SubmitField('Save Changes')

    def validate_companyname(self, field):
        is_seller = True
        if is_seller:
            if field.data and not field.data.strip(): # if empty spaces are filled out in the field
                raise ValidationError('Company name cannot be empty.')
        

@bp.route('/user_address', methods=['GET', 'POST'])
@login_required
def user_address():
    form = ChangeAddressForm()
    form.country.choices = get_country_choices()

    if 'submit' in request.form:
        if (form.companyname.data or 
            form.streetaddress.data or
            form.country.data != current_user.country or 
            form.stateregion.data or
            form.city.data or 
            form.zipcode.data or
            form.phonenumber.data):
            if form.validate_on_submit():
                try:
                    User.update_address(
                        current_user.userkey,
                        form.companyname.data,
                        form.streetaddress.data,
                        form.country.data,
                        form.stateregion.data,
                        form.city.data,
                        form.zipcode.data,
                        form.phonenumber.data
                    )
                    # flash('Your address have been updated.', 'success')
                except Exception as e:
                    flash(str(e), 'error')
                return redirect(url_for('users.user_address'))
    return render_template('user_address.html', form=form)



class BalanceForm(FlaskForm):
    amount = StringField('Amount', validators=[DataRequired()])
    action = HiddenField()
    submit = SubmitField('Continue')


@bp.route('/user_balance', methods=['GET', 'POST'])
@login_required
def manage_user_balance():
    form = BalanceForm()
    if form.validate_on_submit():
        action = form.action.data
        amount = Decimal(form.amount.data)
        if action == 'withdraw':
            if current_user.balance < amount:
                flash('Insufficient funds', 'error')
                return redirect(url_for('users.manage_user_balance'))
            amount = -amount
        new_balance = current_user.balance + amount
        try:
            User.update_balance(current_user.userkey, amount, new_balance)
            # flash('Balance updated successfully', 'success')
        except Exception as e:
            flash(str(e), 'error')
        return redirect(url_for('users.manage_user_balance'))
    return render_template('user_balance.html', form=form)



class BecomeSellerForm(FlaskForm):
    companyname = StringField('Your company name:', validators=[DataRequired()])
    next = HiddenField()
    submit = SubmitField('Continue')

@bp.route('/become_a_seller', methods=['POST'])
@login_required
def become_a_seller():
    become_seller_form = BecomeSellerForm()
    if 'submit' in request.form:
        try:
            User.update_address(userkey=current_user.userkey, companyname=become_seller_form.companyname.data)
            # Seller.register(current_user.userkey, become_seller_form.company_name.data)
            flash('You have successfully become a seller!', 'success')
        except Exception as e:
            flash(str(e), 'error')
    return redirect(become_seller_form.next.data)
    


@bp.route('/upload_profile_image', methods=['POST'])
@login_required
def upload_profile_image():

    def allowed_file(filename):
        # Check the file extension to ensure it's within the allowed types
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

    def get_extension(filename):
        # Extract the file extension
        return '.' + filename.rsplit('.', 1)[1].lower()

    file = request.files['profile_image']
    if file and allowed_file(file.filename):  # Make sure the file exists and is of an allowed type
        unique_id = uuid.uuid4().hex  # Generates a random UUID
        filename = f"user_profile_pic_{current_user.userkey}_{unique_id}{get_extension(file.filename)}"
        filepath = os.path.join(current_app.root_path, 'static', 'img', filename)
        file.save(filepath)
        try:
            User.update_imageurl(current_user.userkey, 'img/'+filename)
        except Exception as e:
            flash(str(e), 'error')
    return redirect(url_for('users.user_profile'))





@bp.app_context_processor
def inject_user_status():
    if not current_user.is_authenticated:
        return {'is_seller': False}
    
    return dict(is_seller = False,
        # is_seller=Seller.is_seller(current_user.userkey), 
        become_seller_form=BecomeSellerForm(obj=current_user))


#     {% for orders in orders %}
#     <p>
#         {% for item in orders %}
#             {{ item }}{% if not loop.last %}, {% endif %}
#         {% endfor %}
#     </p>
# {% endfor %}