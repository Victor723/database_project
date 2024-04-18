from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User


from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    companyname = StringField('Company Name')
    streetaddress = StringField('Street Address')
    city = StringField('City')
    stateregion = StringField('State/Region')
    zipcode = StringField('Zipcode')
    country = StringField('Country')
    phonenumber = StringField('Phone Number')
    # phonenumber = StringField('Phone Number', validators=[
    #     DataRequired(),
    #     Regexp(regex=r'^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$',
    #            message='Invalid US phone number. Format must be XXX-XXX-XXXX with or without the country code.')
    # ])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

    # def validate_phonenumber(form, field):
    #     # Strip all non-numeric characters for the length check
    #     number_only = re.sub(r'[^\d]', '', field.data)
    #     if len(number_only) not in (10, 11):
    #         raise ValidationError('Phone number must be 10 or 11 digits long.')


class UserDetailsForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Changes')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')


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

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Call the register method with all the form fields
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.companyname.data,
                         form.streetaddress.data,
                         form.city.data,
                         form.stateregion.data,
                         form.zipcode.data,
                         form.country.data,
                         form.phonenumber.data): 
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/user_details', methods=['GET', 'POST'])
@login_required
def user_details():
    user_details_form = UserDetailsForm()
    password_form = ChangePasswordForm()
    if request.method == 'POST':
        if user_details_form.validate_on_submit():
            try:
                success = User.update_user_details(
                    current_user.userkey,
                    user_details_form.email.data,
                    user_details_form.firstname.data,
                    user_details_form.lastname.data
                )
                if success:
                    flash('Your account details have been updated.', 'success')
                else:
                    flash('An error occurred while updating your details.', 'error')
            except Exception as e:
                flash(str(e), 'error')
            return redirect(url_for('users.user_details'))

        elif password_form.validate_on_submit():
            try:
                if User.check_password(current_user.userkey, password_form.current_password.data):
                    if User.update_password(current_user.userkey, password_form.new_password.data):
                        flash('Your password has been changed.', 'success')
                    else:
                        flash('Your password has not been changed.', 'error')
                else:
                    flash('Current password is incorrect.', 'error')
            except Exception as e:
                flash(str(e), 'error')
            return redirect(url_for('users.user_details'))

    return render_template('user_details.html', user_details_form=user_details_form, password_form=password_form)

@bp.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    return render_template('user_profile.html')