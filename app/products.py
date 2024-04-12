from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask import jsonify
import datetime
from .models.product import Product
from .models.bid import Bid
from .models.review import ProductReview
from .models.user import User
from .models.purchase import Purchase
from .models.order import Order
#from .models.charity import Charity



from flask import Blueprint
bp = Blueprint('products', __name__)


# class getcount(FlaskForm):
#     user_id = IntegerField('k', validators=[InputRequired('Please enter a number!')])
#     submit = SubmitField('Insert number of most expensive items')









#returns the product with the highest price attribute
@bp.route('/product/expensive/', methods=['GET'])
def products_get_most_expensive():
    k = request.args.get('k', default=5, type=int)
    items = Product.get_most_expensive(k)
    return render_template('product_expensive.html',
                           avail_products=items,
                           mynum=k)
    
#Sorts categories by attribute
@bp.route('/sort/', methods=['GET'])
def products_filter():
    page = int(request.args.get('page', default=1))
    attribute = request.args.get('attribute', default='Most Expensive', type=str)
    if attribute == "Most Expensive":
        items = Product.get_most_expensive()
    elif attribute == "Least Expensive":
        items = Product.get_least_expensive()
    elif attribute == "Highest rating":
        items = Product.get_highest_rating()
    else:
        items = Product.get_expiration()
    return render_template('index.html',
                            avail_products=items,
                            page = page)

#returns product metadata to be displayed in product info page
@bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product_info(product_id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    product = Product.get(product_id)
    #get user
    #currentbid = Bid.get_max_bid(product_id).amount if Bid.get_max_bid(product_id) else product.price
    currentbid = Bid.get_max_bid(product_id).amount if Bid.get_max_bid(product_id) else product.starting_bid


    product_reviews = ProductReview.get_by_pid(product_id)
    total_reviews = ProductReview.get_total_number_by_id(product_id)
    avg_rating = ProductReview.get_average_rating(product_id)
    my_review = ProductReview.get_last_review(product_id, current_user.id)


    charity_id = User.getCharityIdWithProductId(product_id)
    print("this is our charity_id for the given product:")
    print(type(charity_id))
    print(charity_id)
    charity_name = User.getCharityNameGivenCharityId(charity_id)
    print("this is our charity_name for the given product:")
    print(charity_name)


    #charity = getCharityGivenProductId(product_id)


    # if request.method == 'POST':
    #     if request.form['action'] == 'delete_review':
    #         ProductReview.delete_by_id(request.form['review_id'])
    #         product_reviews = ProductReview.get_by_pid(product_id)
    #         total_reviews = ProductReview.get_total_number_by_id(product_id)
    #         avg_rating = ProductReview.get_average_rating(product_id)
    #         my_review = ProductReview.get_last_review(product_id, current_user.id)
    #         return render_template('product_info.html',
    #                        isNewReview=my_review is None,
    #                        my_review=my_review,
    #                        product=product,
    #                        product_reviews=product_reviews,
    #                        total=total_reviews,
    #                        average=avg_rating)


    page = int(request.args.get('page', default=1))


    if request.method == 'POST':
        
        #User requests to delete review
        if request.form['action'] == 'delete_review':
            ProductReview.delete_by_id(request.form['review_id'])
            product_reviews = ProductReview.get_by_pid(product_id)
            total_reviews = ProductReview.get_total_number_by_id(product_id)
            avg_rating = ProductReview.get_average_rating(product_id)
            my_review = ProductReview.get_last_review(product_id, current_user.id)
            return render_template('product_info.html',
                            isNewReview=my_review is None,
                            my_review=my_review,
                            product=product,
                            product_reviews=product_reviews,
                            total=total_reviews,
                            average=avg_rating,
                            page=page)


    
    
    if request.method == 'POST' and current_user.is_authenticated: #verifies that user is authenticated
        #User downvotes product
        if request.form['action'] == 'downvote':
            if int(request.form['likes']) > 0:
                ProductReview.update_upvote_for_id(int(request.form['review_id']), -1, current_user.id)
                product_reviews = ProductReview.get_by_pid(product_id)
                total_reviews = ProductReview.get_total_number_by_id(product_id)
                avg_rating = ProductReview.get_average_rating(product_id)
                my_review = ProductReview.get_last_review(product_id, current_user.id)
        #User upvotes product
        elif request.form['action'] == 'upvote':
            ProductReview.update_upvote_for_id(int(request.form['review_id']), 1, current_user.id)
            product_reviews = ProductReview.get_by_pid(product_id)
            total_reviews = ProductReview.get_total_number_by_id(product_id)
            avg_rating = ProductReview.get_average_rating(product_id)
            my_review = ProductReview.get_last_review(product_id, current_user.id)
        #User bids on product
        elif request.form['action'] == 'bid': 
            bid_amount = float(request.form.get('bidAmount'))
            print(bid_amount)
            user_id = current_user.id   
            print("currentbid: "+str(currentbid))
            print("bid_amount: "+str(bid_amount))
            #print("bid_amt: "+str(bid_amt))
            #if bid_amount>currentbid and bid_amount<=current_user.balance:
            if bid_amount>currentbid and bid_amount<=current_user.balance and bid_amount < product.buy_now: # only allow user to make valid bid if > currentbid, they can afford it, and less than buy_now
            #if bid_amount>currentbid and bid_amount<=current_user.balance: #verifies bid is greater than current max bid and user has enough money
                Bid.add_bid(user_id, product_id, bid_amount, datetime.datetime.now())
                #Product.change_price(product.id, bid_amount)
                flash('Price Changed', "info")
                #product.price = bid_amount
            elif bid_amount>current_user.balance:
                product.price = bid_amount
            elif bid_amount>current_user.balance: #if user doesn't have enough money
                flash("Insufficient Funds!", "warning")
            elif bid_amount<currentbid: #if bid is less than current bid price
                flash("Your bid must be higher than the current bid!", "warning")
            elif bid_amount >= product.buy_now:
                flash("Current bid is equal to or exceeds the Buy Now price. Buy Now if interested!", "warning")
        else:
            return redirect(url_for('users.login'))
        # STILL DO: update the current id in your database


    print("charity_id being passed from product_info() endpoint")
    print(charity_id)

    #if charity_id == None: # then, the charity info for the product that was bought can only be found in Orders
        # get purchase id given product id
        #purchase_id = Purchase.get_purchase_id_by_pid(product_id)
        #charity_user_id = Order.get_seller_id_by_purchase_id(purchase_id)
        #charity_id = Charity.get_charity_id_by_user_id(charity_user_id)


       #TODO: get charityid given userid

    if charity_id == None: # this condition is only True ONLY when the product is no longer in the charity's inventory; charity_id can only be accessed through Orders and Purchases.
        print("pid: ")
        print(product_id)
        purchase_id = Purchase.get_purchase_id_by_pid(product_id)
        print("purchase_id:")
        print(purchase_id)

        charity_id = Order.get_seller_id_by_purchase_id(purchase_id) # TODO: Figure out why the sellerId is not getting returned properly
        print("charit_id after getting from Orders table:")
        print(charity_id)


        charity_name = User.getCharityNameGivenCharityId(charity_id)
        print("charity_user_id:")
        #print(charity_user_id)
        # charity_id = Charity.get_charity_id_by_user_id(charity_user_id)



    max_bid = Bid.get_max_bid(product_id).amount if Bid.get_max_bid(product_id) else product.starting_bid


    return render_template('product_info.html',
                            isNewReview=my_review is None,
                            my_review=my_review,
                            product=product,
                            product_reviews=product_reviews,
                            total=total_reviews,
                            average=avg_rating,
                            page=page,
                            charity_id = charity_id,
                            charity_name = charity_name,
                            max_bid = max_bid)
