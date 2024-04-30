import re
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, json
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
import requests, os, uuid
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal

from .models.user import User
from .models.seller import Seller
from.models.order import Order
from .models.productreview import ProductReview
from .models.sellerreview import SellerReview

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('EMAIL', validators=[DataRequired(), Email()])
    password = PasswordField('PASSWORD', validators=[DataRequired()])
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



class RequiredIfSeller(object): # makes a field required if the register_as_seller field is set to True.
    def __init__(self, message=None):
        if not message:
            message = 'This field is required.'
        self.message = message

    def __call__(self, form, field):
        if form.register_as_seller.data:
            if not field.data or not field.data.strip():
                raise ValidationError(self.message)
            
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    company_name = StringField('Company Name', validators=[RequiredIfSeller()])
    street_address = StringField('Street Address', validators=[RequiredIfSeller()])
    country = StringField('Country', validators=[RequiredIfSeller()])
    state_region = StringField('Region / State', validators=[RequiredIfSeller()])
    city = StringField('City', validators=[RequiredIfSeller()])
    zip_code = StringField('Zip Code', validators=[RequiredIfSeller()])
    phone_number = StringField('Phone Number', validators=[RequiredIfSeller()])
    register_as_seller = BooleanField('Register as a seller')  # Checkbox to register as a seller
    submit = SubmitField('Sign up')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

def get_country_choices():
    url = "https://restcountries.com/v3.1/all"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        countries = response.json()
        country_choices = [(country['cca2'], country['name']['common']) for country in countries 
                           if 'cca2' in country and 'name' in country]
        # add one empty string pair as placeholder and return
        return [("","")] + sorted(country_choices, key=lambda choice: choice[1]) 
    except requests.RequestException as e:
        print(f"Error fetching countries: {e}")
        return [] 
    


@bp.route('/user_register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    form.country.choices = get_country_choices()
    if form.validate_on_submit():
        checked = form.register_as_seller.data
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        company_name = form.company_name.data if checked else None
        street_address = form.street_address.data if checked else None
        city = form.city.data if checked else None
        state_region = form.state_region.data if checked else None
        zip_code = form.zip_code.data if checked else None
        country = form.country.data if checked else None
        phone_number = form.phone_number.data if checked else None
        user = User.register(email, password, first_name, last_name, company_name, street_address, 
                             city, state_region, zip_code, country, phone_number)
        if user: 
            if checked:
                sellerkey = Seller.find_max_sellerkey() + 1  # Get the next available seller key
                Seller.register(sellerkey, user.user_key, user.company_name, date.today())

            login_user(user) # help users skip log in once registered for the first time
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index.index')
            return redirect(next_page)
        
    return render_template('user_register.html', title='Register', form=form)



@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))



class UserDetailsForm(FlaskForm):
    first_name = StringField('First Name', validators=[])
    last_name = StringField('Last Name', validators=[])
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
            if (user_details_form.email.data or user_details_form.first_name.data or user_details_form.last_name.data):
                if user_details_form.validate_on_submit():
                    try:
                        User.update_user_details(
                            current_user.user_key,
                            user_details_form.email.data,
                            user_details_form.first_name.data,
                            user_details_form.last_name.data
                        )
                    except Exception as e:
                        flash(str(e), 'error')
                    return redirect(url_for('users.user_details'))
        if 'submit_password' in request.form and password_form.validate_on_submit():
            try:
                if User.check_password(current_user.user_key, password_form.current_password.data):
                    User.update_password(current_user.user_key, password_form.new_password.data)
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
    user_order_counts = Order.get_order_counts(current_user.user_key)
    current_app.logger.info(f"{current_user.user_key} ") 
    return render_template('user_profile.html', user_order_counts=user_order_counts)


class NonEmptyValidator:
    def __init__(self, message=None):
        if not message:
            message = 'This field cannot be empty.'
        self.message = message

    def __call__(self, form, field):
        if field.data and not field.data.strip():
            raise ValidationError(self.message)


class OptionalIfNoInputOrRegex:
    def __init__(self, regex, message=None):
        self.regex = re.compile(regex)
        self.message = message

    def __call__(self, form, field):
        if not field.data: # if empty
            return
        
        match = self.regex.match(field.data or '')
        if not match:
            message = self.message
            if message is None:
                message = field.gettext('Invalid input.')
            raise ValidationError(message)

class ChangeAddressForm(FlaskForm):
    company_name = StringField('Company Name', validators=[NonEmptyValidator()])
    street_address = StringField('Street Address', validators=[NonEmptyValidator()])
    country = StringField('Country', validators=[NonEmptyValidator()])
    state_region = StringField('Region / State', validators=[NonEmptyValidator()])
    city = StringField('City', validators=[NonEmptyValidator()])
    zip_code = StringField('Zip Code', validators=[NonEmptyValidator()])
    phone_number = StringField('Phone Number', validators=[
        OptionalIfNoInputOrRegex(
            regex=r'^(?:\+?1\s*(?:[.-]\s*)?)?(?:(\(\s*\d{3}\s*\))|\d{3})\s*(?:[.-]\s*)?\d{3}\s*(?:[.-]\s*)?\d{4}$',
            message='Invalid phone number; Format must be XXX-XXX-XXXX or +1 XXX-XXX-XXXX; "-" is optional'
        )
    ])
    submit = SubmitField('Save Changes')


@bp.route('/user_address', methods=['GET', 'POST'])
@login_required
def user_address():
    form = ChangeAddressForm()
    form.country.choices = get_country_choices()
    if 'submit' in request.form:
        if (form.company_name.data or 
            form.street_address.data or
            form.country.data != current_user.country or 
            form.state_region.data or
            form.city.data or 
            form.zip_code.data or
            form.phone_number.data):
            if form.validate_on_submit():
                try:
                    User.update_address(
                        current_user.user_key,
                        form.company_name.data,
                        form.street_address.data,
                        form.country.data,
                        form.state_region.data,
                        form.city.data,
                        form.zip_code.data,
                        form.phone_number.data
                    )
                except Exception as e:
                    flash(str(e), 'error')
                return redirect(url_for('users.user_address'))
    return render_template('user_address.html', form=form)



class BalanceForm(FlaskForm):
    amount = StringField('Amount', validators=[DataRequired()])
    action = HiddenField()
    submit = SubmitField('Continue')

def fill_missing_months(monthly_expenditure):
    # Start from one year ago up to the current month
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    
    # Create a set of all months in the range
    all_months = set()
    current_date = start_date
    while current_date <= end_date:
        all_months.add((current_date.year, current_date.month))
        current_date += timedelta(days=31)  # Move to the next month
    
    # Create a default dictionary with zero expenditure for each month
    filled_expenditure = {(year, month): 0 for year, month in all_months}
    
    # Update the dictionary with actual expenditures
    for year, month, amount in monthly_expenditure:
        filled_expenditure[(int(year), int(month))] = float(amount)
    
    # Convert the dictionary back to a sorted list of tuples
    sorted_filled_expenditure = sorted(filled_expenditure.items(), key=lambda x: x[0])
    return [(year, month, amount) for ((year, month), amount) in sorted_filled_expenditure]

def iso_year_start(iso_year):
    "The gregorian calendar date of the first day of the given ISO year"
    fourth_jan = datetime(iso_year, 1, 4)
    delta = timedelta(fourth_jan.isoweekday()-1)
    return fourth_jan - delta 

def iso_to_gregorian(iso_year, iso_week, iso_day):
    "Gregorian calendar date for the given ISO year, week and day"
    year_start = iso_year_start(iso_year)
    return year_start + timedelta(weeks=iso_week-1, days=iso_day-1)

def fill_missing_weeks(weekly_expenditure):
    # Determine the ISO year and week number for today and one year ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    start_iso_year, start_iso_week, _ = start_date.isocalendar()
    end_iso_year, end_iso_week, _ = end_date.isocalendar()
    
    # Generate all weeks between start and end date
    all_weeks = set()
    current_iso_year, current_iso_week = start_iso_year, start_iso_week
    while (current_iso_year, current_iso_week) <= (end_iso_year, end_iso_week):
        all_weeks.add((current_iso_year, current_iso_week))
        # Move to the next week
        current_date = iso_to_gregorian(current_iso_year, current_iso_week, 7) + timedelta(days=1)
        current_iso_year, current_iso_week, _ = current_date.isocalendar()
    
    # Create a default dictionary with zero expenditure for each week
    filled_expenditure = {(year, week): 0 for year, week in all_weeks}
    
    # Update the dictionary with actual expenditures
    for year, week, amount in weekly_expenditure:
        filled_expenditure[(int(year), int(week))] = float(amount)
    
    # Convert the dictionary back to a sorted list of tuples
    sorted_filled_expenditure = sorted(filled_expenditure.items(), key=lambda x: x[0])
    return [(year, week, amount) for ((year, week), amount) in sorted_filled_expenditure]


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
        try:
            User.update_balance(current_user.user_key, amount)
        except Exception as e:
            flash(str(e), 'error')
        return redirect(url_for('users.manage_user_balance'))
    
    weekly_expenditure = Order.get_weekly_expenditure(current_user.user_key)
    monthly_expenditure = Order.get_monthly_expenditure(current_user.user_key)
    if weekly_expenditure and monthly_expenditure:
        filled_weekly_expenditure = fill_missing_weeks(weekly_expenditure)
        filled_monthly_expenditure = fill_missing_months(monthly_expenditure) 
    else:
        filled_weekly_expenditure = []
        filled_monthly_expenditure = []
        
    return render_template('user_balance.html', 
                           form=form, 
                           filled_monthly_expenditure=filled_monthly_expenditure,
                           filled_weekly_expenditure=filled_weekly_expenditure)


@bp.route('/update_spending_summary', methods=['GET'])
@login_required
def update_spending_summary():
    start_date = request.args.get('start', type=str)
    end_date = request.args.get('end', type=str)
    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            spending_summary = Order.get_user_spending_summary(current_user.user_key, start_date, end_date)
            spending_summary = [{'category': ele[0], 'amount': float(ele[1])} for ele in spending_summary]
            spending_summary = sorted(spending_summary, key=lambda x: x['amount'], reverse=True)
            spending_sum = sum(ele['amount'] for ele in spending_summary[1:])
            for i in range(1,len(spending_summary)):
                spending_summary[i]['percentage'] = round((spending_summary[i]['amount'] / spending_sum)*100, 1)
            # current_app.logger.info(f"{total_spending}") 
            return jsonify(spending_summary)
        except Exception as e:
            current_app.logger.error(f'Error fetching spending summary: {e}')
            return jsonify({'error': 'Failed to fetch spending summary'}), 500
    return jsonify({'error': 'Invalid parameters'}), 400


@bp.route('/become_a_seller', methods=['POST'])
@login_required
def become_a_seller():
    can_become_seller = all([
        current_user.street_address,
        current_user.country,
        current_user.state_region,
        current_user.city,
        current_user.zip_code,
        current_user.phone_number,
        current_user.company_name
    ])
    if can_become_seller:
        if not Seller.get_sellerkey(current_user.user_key):  # if current user is not already a seller
            try:
                nxt_sellerkey = Seller.find_max_sellerkey() + 1  # Get the next available seller key
                Seller.register(sellerkey=nxt_sellerkey, userkey=current_user.user_key, 
                                companyname=current_user.company_name, registrationdate=date.today())
                return jsonify({'success': True, 'message': 'You have successfully become a seller!'})
            except Exception as e:
                current_app.logger.error('Error registering seller: %s', e)
                return jsonify({'success': False, 'message': 'Unknown error occurred while registering.'})
        else:
            return jsonify({'success': True, 'message': 'You are already registered as a seller.'})
    else:
        return jsonify({'success': False, 'message': 'Please complete all the address fields to register as a seller.'})
    

@bp.route('/Switch_to_seller', methods=['GET','POST'])
@login_required
def switch_to_seller():
    sellerkey = Seller.get_sellerkey(current_user.user_key)
    if sellerkey is None: # just in case. Usually users can't see this button if they aren't sellers
        flash('You are not a seller. Register first.', 'info')
        return redirect(url_for('users.user_profile'))
    else:
        seller_info = Seller.get_seller_information(sellerkey)
        seller_name = seller_info[0]['first_name'] + seller_info[0]['last_name']
        return render_template('seller_homepage.html', seller_name=seller_name, seller_key=sellerkey)


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
        filename = f"user_profile_pic_{current_user.user_key}_{unique_id}{get_extension(file.filename)}"
        filepath = os.path.join(current_app.root_path, 'static', 'img', filename)
        file.save(filepath)
        try:
            User.update_image_url(current_user.user_key, 'img/'+filename)
        except Exception as e:
            flash(str(e), 'error')
    return redirect(url_for('users.user_profile'))


@bp.route('/public_view', methods=['GET','POST'])
def public_user_profile():

    user_key = 3

    is_seller = True if Seller.get_sellerkey(user_key) else False
    user_info = User.get_for_public_view(user_key, is_seller)
    # current_app.logger.info(f"{user_info} {is_seller}")

    user_review = ProductReview.get_user_reviews(user_key)
    seller_review = SellerReview.get_user_reviews(user_key)
    # current_app.logger.info(f"{user_review} {seller_review}")

    return render_template('user_public_view.html', user_info=user_info, user_review=user_review, seller_review=seller_review)


@bp.app_context_processor
def inject_user_status():
    if not current_user.is_authenticated:
        return {'is_seller': False}
    
    is_seller = True if Seller.get_sellerkey(current_user.user_key) else False
    # return dict(is_seller=is_seller, become_seller_form=BecomeSellerForm(obj=current_user))
    return dict(is_seller=is_seller)

