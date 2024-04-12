from flask import render_template
from flask_login import current_user
import datetime
from flask import redirect, url_for


from .models.product import Product
from .models.purchase import Purchase
from .models.sells import SoldItem
from .models.order import Order
from .models.bid import Bid
from .models.user import User


from flask import Blueprint
bp = Blueprint('purchased', __name__) #changed to purchased


from humanize import naturaltime


def humanize_time(dt):
    print(dt)
    return naturaltime(datetime.datetime.now() - dt)

#returns purchase history
@bp.route('/purchased')
def purchased():
    # get all available products for sale:
    products = Product.get_all(True)
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
        bids = Bid.get_bids(current_user.id)
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('purchased.html', #change to purchased.html and add humanize
                            avail_products=products,
                            purchase_history=purchases,
                            bid_history = bids,
                            humanize_time=humanize_time
                            )
    
#adds purchase to purchase history
@bp.route('/purchased/add/<int:product_id>', methods=['POST'])
def purchased_add(product_id):
    if current_user.is_authenticated and current_user.balance >= Product.getBuyNow(product_id): #Product.getPrice(product_id):
        newPurchase = Purchase.add_purchase(current_user.id, product_id, datetime.datetime.now()) #how to get the current time


        #TODO: Implement Orders.add_order() method
        charityId = User.getCharityIdWithProductId(product_id)
        #TODO: make method to get the timePurchased (which will be same as date_placed)
        date_placed = newPurchase.time_purchased
        #TODO: make method to get the cost of the item
        cost = newPurchase.price


        purchaseId = newPurchase.id


        productName = newPurchase.name


        Order.add_order(purchaseId, productName, current_user.id, charityId, date_placed, cost, False)


        SoldItem.remove_charity_item(product_id) # Removes item from Sells table, and then Product Table


        return redirect(url_for('purchased.purchased'))
    else:
        return redirect(url_for('users.updateBalance'))