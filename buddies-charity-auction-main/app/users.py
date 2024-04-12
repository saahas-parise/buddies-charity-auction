from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.product import Product
from .models.purchase import Purchase
from .models.bid import Bid

from humanize import naturaltime
import datetime
def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)
from flask import Blueprint
bp = Blueprint('users', __name__)

#Form where logs in using credentials
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
#Form for user to deposit / withdraw money
class BalanceForm(FlaskForm):
    amount = IntegerField('Amount', validators=[DataRequired()])
    deposit = SubmitField('Deposit')
    withdraw = SubmitField('Withdraw')
    
#Login method
@bp.route('/login', methods=['GET', 'POST'])
def login():
    print("login called")
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password') # I COMMENTED THIS OUT 
            return redirect(url_for('users.login')) # I COMMENTED THIS OUT
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

#Form for registering a new User
class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address =  StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])

    is_charity = BooleanField('Register as Charity?', false_values=()) # if checkbox is unchecked, no data has been sent ==> we want this to evaluate to False!
    
    #NEW FIELD: IF user wants to be a Charity
    charity_name = StringField('Charity Name')

    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')
        
#Form for updating user info
class UpdateForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    #address =  StringField('Address', validators=[DataRequired()])    
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

#Method for registering a new user
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    print("before validate_on_submit")
    if form.validate_on_submit():
        print("validate_on_submit is True")
        #if form.is_charity.data:
        if form.is_charity.data:
            # Register as Charity
            print("form.is_charity")
            if User.register_as_charity(form.email.data,
                                         form.password.data,
                                         form.firstname.data,
                                         form.lastname.data,
                                         form.charity_name.data,
                                         form.address.data):
                print("register_as_charity condition passed")
                flash('Congratulations, you are now a registered charity!')
                return redirect(url_for('users.login'))
        else:
            # Register as regular user
            print("reached the last else statement in register()")
            if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         form.address.data):
                print("reached inside the User.register if statement")
                flash('Congratulations, you are now a registered user!')
                return redirect(url_for('users.updateBalance'))

    print("not registered successfully :(((")
    return render_template('register.html', title='Register', form=form)

#Method for updating user info
@bp.route('/Update', methods=['GET', 'POST'])
def update():
    form = UpdateForm()
    if form.validate_on_submit():
        if User.update(current_user.id,
                         form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data,
                         current_user.balance):
            flash('Congratulations, you have updated your information!')
        return redirect(url_for('users.updateBalance'))
    products = Product.get_all(True)
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    return render_template('account.html', title = 'Update', form=form, avail_products=products,
                           purchase_history=purchases,
                           humanize_time=humanize_time)


 #method for withdrawing / depositing   
@bp.route('/account', methods=['GET', 'POST'])   
def updateBalance():
    if not current_user.is_authenticated:
        return redirect(url_for('users.update'))
    id = current_user.id
    form =BalanceForm()
    if form.validate_on_submit: #when the user submits
        amount = form.amount.data
        if amount: 
            flash("$$$$ Balance Updated $$$$", "info") #notify the user
            if form.deposit.data:
                new_balance = User.get_balance(id) + amount #increment
            elif form.withdraw.data:
                new_balance = max(User.get_balance(id) - amount,0) #decrement
            User.update_balance(id, new_balance)  
            return redirect(url_for('users.updateBalance'))  #refreshes page 
    else:
        flash("No balance entered!", "Warning")
    products = Product.get_all(True)
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
        bids = Bid.get_bids(current_user.id)
    else:
        purchases = None
    return render_template('account.html', form=form, avail_products=products,
                           purchase_history=purchases,
                           humanize_time=humanize_time,
                           bid_history = bids)
#logs the user out
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))
