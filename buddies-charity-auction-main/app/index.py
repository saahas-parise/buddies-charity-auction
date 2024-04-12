from flask import render_template, request, url_for
from flask_login import login_user, logout_user, current_user
import datetime
from flask import request, jsonify
from .models.charity import Charity


from flask import redirect, flash




from .models.product import Product
from .models.purchase import Purchase
from .models.order import Order
from .models.sells import SoldItem




from .models.sells import SoldItem


from .models.user import User




from flask import Blueprint
bp = Blueprint('index', __name__) #changed to purchased
from humanize import naturaltime


def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)


def apply_filters(products, category_filter, price_range_filter):
    # Implement filter logic
    filtered_products = products
    # Apply category filter
    if category_filter and category_filter != 'All Categories':
        filtered_products = [product for product in filtered_products if product.catergory == category_filter]


    # Apply price range filter
    if price_range_filter:
        min_price, max_price = map(int, price_range_filter.split('-'))
        #filtered_products = [product for product in filtered_products if min_price <= product.price <= max_price]
        filtered_products = [product for product in filtered_products if min_price <= product.buy_now <= max_price]


    return filtered_products

# homepage
@bp.route('/')
def index():

    # get all available products for sale:
    #products = Product.get_all(True)
    products = Product.get_available_and_not_purchased()


    # Retrieve the selected category filter and price range filter from the URL
    category_filter = request.args.get('category', default='', type=str)
    price_range_filter = request.args.get('priceRange', default='', type=str)


    # Apply the filters to the products based on the selected category and price range
    filtered_products = apply_filters(products, category_filter, price_range_filter)




    page = int(request.args.get('page', default=1))



    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('welcome.html', #change to purchased.html and add humanize
                            avail_products=filtered_products,
                            purchase_history=purchases,
                            humanize_time=humanize_time,
                            page=page)

#displays all available products for sale with an option to filter by price, rating etc
@bp.route('/products')
def products():
        # get all available products for sale:
    #products = Product.get_all(True)
    products = Product.get_available_and_not_purchased()

    # Retrieve the selected category filter and price range filter from the URL
    category_filter = request.args.get('category', default='', type=str)
    price_range_filter = request.args.get('priceRange', default='', type=str)


    # Apply the filters to the products based on the selected category and price range
    filtered_products = apply_filters(products, category_filter, price_range_filter)




    page = int(request.args.get('page', default=1))



    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('index.html', #change to purchased.html and add humanize
                            avail_products=filtered_products,
                            purchase_history=purchases,
                            humanize_time=humanize_time,
                            page=page)




#searches the products/sellers based on a given search query
@bp.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('search_query')
    search_type = request.args.get('search_type')
    page = int(request.args.get('page', default=1))
    # Add logic to handle the search query based on the search type
    if search_type == 'product':
        # Search products by name or other attributes
        results = Product.search_by_name(search_query)
    elif search_type == 'seller':
        # Search sellers by name or other attributes
        results = SoldItem.search_by_seller(search_query)
    else:
        # Handle other search types or show an error message
        flash('Invalid search type', 'error')
        return redirect(url_for('index.index'))


    # Render the search results page
    return render_template('index.html', avail_products=results,
                            page=page)








#gets products for sale for a charity 5 by default
@bp.route('/sells/', methods = ['GET'])
def sells():
    charityId = request.args.get('charityId', default=5, type=int)
    print("in function")

    items = SoldItem.get_charity_items(int(charityId)) # array of


    # print(type(items[0]))
    # print("items is " + str(items[0]))


    #items = [row[0] for row in items] # list of strings


    #for item in items:
    #   print(item)


    # need to convert items to type list


    return render_template('seller_products.html',
    avail_products = items,
    mynum= charityId)

#for charities to add new items to their inventory
@bp.route('/sells/inventory', methods = ['GET', 'POST'])
def seller_inventory():
    #charityId = request.args.get('charityId', default=5, type=int)
    #print("in function")

    #items = SoldItem.get_charity_items(int(charityId))


    #if current_user.is_authenticated: #and User.isCharity(current_user.id):
    if current_user.is_authenticated and User.isCharity(current_user.id):
        # WishlistItem.add(current_user.id, product_id, datetime.datetime.now())
        # return redirect(url_for('wishlist.wishlist'))


        print(current_user.id)


        charityId = User.getCharityId(current_user.id) # TO DO: Need to make sure that this can be cast as an int
        name = User.getCharityName(current_user.id)

        items = SoldItem.get_charity_items(int(charityId))

        under_fifty = 0
        over_fifty = 0

        for item in items:
            if item.buy_now <= 50:
                under_fifty += 1
            else:
                over_fifty += 1

        # Get the top 5 highest-rated items
        top_rated_items = SoldItem.get_top_rated_items(charityId, 5)

        sorted_expiration = SoldItem.get_earliest_expiring_items(charityId, limit=5)


        if request.method == 'POST':
            action = request.form.get('action')

            if action == 'applyFilters':

                sort_price = request.form.get('selectedSortPrice', default='default', type=str)

                items = SoldItem.get_charity_items(int(charityId))

                under_fifty = 0
                over_fifty = 0

                for item in items:
                    if item.buy_now <= 50:
                        under_fifty += 1
                    else:
                        over_fifty += 1

                # items = [Product(*row) for row in rows]

                if sort_price == '0-50':
                    #items = sorted(items, key=lambda order: order.productName)

                    top_rated_items = SoldItem.get_top_rated_items_less_than_fifty(charityId, 5)
                    sorted_expiration = SoldItem.get_earliest_expiring_items_under_fifty(charityId, 5)

                    items = [product for product in items if 0 <= product.buy_now <= 50]

                elif sort_price == '50+':
                    top_rated_items = SoldItem.get_top_rated_items_greater_than_fifty(charityId, 5)

                    sorted_expiration = SoldItem.get_earliest_expiring_items_over_fifty(charityId, 5)
                    
                    items = [product for product in items if 50 < product.buy_now]

                print("Applying filters")




                return render_template('seller_inventory.html',
                avail_products = items,
                mynum= charityId,
                charityName = name,
                under_fifty = under_fifty,
                over_fifty = over_fifty,
                sorted_expiration = sorted_expiration
                )


        



        return render_template('seller_inventory.html',
        avail_products = items,
        mynum= charityId,
        charityName = name,
        under_fifty = under_fifty,
        over_fifty = over_fifty,
        sorted_expiration = sorted_expiration)
    else:
        return redirect(url_for('index.index'))




   # return render_template('seller_inventory.html',
   # avail_products = items,
   # mynum= charityId)




#renders charity info page for a given charity
@bp.route('/infopage/', methods=['GET', 'POST'])
def charity_info():
    charity_id = request.args.get('charity_id')
    if charity_id is None:
        if current_user.is_authenticated and User.isCharity(current_user.id):
            charity_id = current_user.getCharityId(current_user.id)
        else:
            flash("Unauthorized access.")
            return redirect(url_for('index'))

    # Retrieve charity information
    charityDescription = User.getCharityDescriptionGivenCharityId(charity_id)
    name = User.getCharityNameGivenCharityId(charity_id)
    items = SoldItem.get_charity_items(int(charity_id))

    message_threads = []
    if current_user.is_authenticated and User.isCharity(current_user.id):
        # Fetch message threads if the current user is the charity
        try:
            message_threads = Charity.get_message_threads(charity_id)
            print('Message Threads:', message_threads)
        except Exception as e:
            print("Error retrieving message threads:", e)

    return render_template('charity_info.html',
                           avail_products=items,
                           charity_id=charity_id,
                           charityName=name,
                           charityDescription=charityDescription,
                           message_threads=message_threads)


#changes charity description
@bp.route('/change_charity_description', methods = ['GET', 'POST'])
def change_charity_description():
    print("reached change_charity_description() method in index.py")




    if current_user.isCharity(current_user.id): #and current_user.getCharityId(current_user.id) == charity_id:
        charity_id = current_user.getCharityId(current_user.id)


        new_description = request.form.get('newDescription')
        print(new_description)


        # Validate new_description if necessary


        # Update the charity's description
        User.update_charity_description(charity_id, new_description)


        #flash('Charity description updated successfully.', 'success')
        return redirect(url_for('index.charity_info', charity_id=charity_id))


    flash('You do not have permission to change this charity\'s description.', 'error')
    return redirect(url_for('users.account'))







#shows items that have been sold
@bp.route('/sells/orders', methods = ['GET', 'POST'])
def seller_orders():
    #charityId = request.args.get('charityId', default=5, type=int)
    #print("in function")

    #items = SoldItem.get_charity_items(int(charityId))


    #if current_user.is_authenticated: #and User.isCharity(current_user.id):
    if current_user.is_authenticated and User.isCharity(current_user.id):
        # WishlistItem.add(current_user.id, product_id, datetime.datetime.now())
        # return redirect(url_for('wishlist.wishlist'))


        print(current_user.id)


        charityId = User.getCharityId(current_user.id) # TO DO: Need to make sure that this can be cast as an int




        name = User.getCharityName(current_user.id)
        
        #items = SoldItem.get_charity_items(int(charityId))
        #items = SoldItem.get_charity_orders(int(charityId))

        # TODO: need to make method to get order items in "reverse chronological order" ==> earliest to latest
        items = SoldItem.get_charity_orders_reverse_chronological(int(charityId))

        # Apply sorting if a specific order is selected


        # Get the selected sorting order from the URL
        sort_order = request.form.get('selectedSortOrder', default='default', type=str)
        print("value of sort_order")
        print(sort_order)

        if sort_order == 'alphabetical':
            items = sorted(items, key=lambda order: order.productName)

        if request.method == 'POST':

            action = request.form.get('action')

            if action == 'changeStatus':
                print("value of status before if statement")
                print(request.form['order_status'])
                #newStatus = bool(request.form['order_status'])
                newStatus = request.form['order_status']
                print(newStatus)
                
                if newStatus == "True":
                    newStatus = False
                else:
                    newStatus = True


                #newStatus = not request.form['order_status']
                print("value of newStatus in seller_orders()")
                print(newStatus)
                Order.change_fulfillment_status(request.form['order_id'],newStatus)
                #items = SoldItem.get_charity_orders(int(charityId))
                items = SoldItem.get_charity_orders_reverse_chronological(int(charityId))

            elif action == 'applyFilters':
                items = SoldItem.get_charity_orders_reverse_chronological(int(charityId))

                if sort_order == 'alphabetical':
                    items = sorted(items, key=lambda order: order.productName)

                print("Applying filters")


        fulfilled_count = SoldItem.get_fulfilled_orders_count(charityId)
        unfulfilled_count = SoldItem.get_unfulfilled_orders_count(charityId)


        top_categories = SoldItem.get_top_categories(charityId, 5)

        return render_template('seller_orders.html',
                            avail_orders=items,
                            fulfilled_count=fulfilled_count,
                            unfulfilled_count=unfulfilled_count,
                            mynum=charityId,
                            charityName=name,
                            top_categories=top_categories)


        # return render_template('seller_orders.html',
        # avail_orders = items,
        # mynum= charityId,
        # charityName = name)
    else:
        return redirect(url_for('index.index'))

#removes items from seller list
@bp.route('/sells/orders/<string:filter>', methods=['GET', 'POST'])
def view_orders(filter):
    
    #charity_id = current_user.id  # Assuming the current user is a charity
    charity_id = User.getCharityId(current_user.id) # TO DO: Need to make sure that this can be cast as an int
    name = User.getCharityName(current_user.id)



    sort_order = request.form.get('selectedSortOrder', default='default', type=str)
    top_categories = SoldItem.get_top_categories(charity_id, 5)

    if filter == 'all':
        orders = SoldItem.get_charity_orders_reverse_chronological(charity_id)
    elif filter == 'fulfilled':
        # Fetch only fulfilled orders
        orders = SoldItem.get_charity_orders_reverse_chronological(charity_id)
        orders = [order for order in orders if order.status]
        top_categories = SoldItem.get_top_categories_with_status(charity_id, 5, "true")
    elif filter == 'unfulfilled':
        # Fetch only unfulfilled orders
        orders = SoldItem.get_charity_orders_reverse_chronological(charity_id)
        orders = [order for order in orders if not order.status]
        top_categories = SoldItem.get_top_categories_with_status(charity_id, 5, "false")
    else:
        # Invalid filter, redirect to all orders
        flash('Invalid filter, redirecting to all orders.')
        return redirect(url_for('order.view_orders', filter='all'))

            # elif action == 'applyFilters':
            #     items = SoldItem.get_charity_orders_reverse_chronological(int(charityId))

            #     if sort_order == 'alphabetical':
            #         items = sorted(items, key=lambda order: order.productName)

    if request.method == "POST":


            action = request.form.get('action')


            if action == 'changeStatus':
                print("value of status before if statement: FILTER ENDPOINT ADDITION")
                print(request.form['order_status'])
                #newStatus = bool(request.form['order_status'])
                newStatus = request.form['order_status']
                print(newStatus)
                
                if newStatus == "True":
                    newStatus = False
                else:
                    newStatus = True


                #newStatus = not request.form['order_status']
                print("value of newStatus in view_orders()")
                print(newStatus)
                Order.change_fulfillment_status(request.form['order_id'],newStatus)

            elif action == 'applyFilters':
                orders = SoldItem.get_charity_orders_reverse_chronological(int(charity_id))



                sort_order = request.form.get('selectedSortOrder', default='default', type=str)

                top_categories = SoldItem.get_top_categories(charity_id, 5)

                print("this is the value of the drop down filter:")
                print(sort_order)

                if sort_order == 'alphabetical':
                    orders = sorted(orders, key=lambda order: order.productName)
                    print("sorted alphabetically!!!!!!")

                if filter == 'fulfilled': 
                    orders = [order for order in orders if order.status]
                    top_categories = SoldItem.get_top_categories_with_status(charity_id, 5, "true")
                elif filter == 'unfulfilled': 
                    orders = [order for order in orders if not order.status]
                    top_categories = SoldItem.get_top_categories_with_status(charity_id, 5, "false")


                return render_template('seller_orders.html', 
                    avail_orders=orders,
                    mynum=charity_id, 
                    charityName=name)

            if filter == 'all':
                orders = SoldItem.get_charity_orders_reverse_chronological(charity_id)
                top_categories = SoldItem.get_top_categories(charity_id, 5)

                
            elif filter == 'fulfilled':
                # Fetch only fulfilled orders
                orders = SoldItem.get_charity_orders_reverse_chronological(charity_id)
                orders = [order for order in orders if order.status]
                top_categories = SoldItem.get_top_categories_with_status(charity_id, 5, "true")

            elif filter == 'unfulfilled':
                # Fetch only unfulfilled orders
                orders = SoldItem.get_charity_orders_reverse_chronological(charity_id)
                orders = [order for order in orders if not order.status]
                top_categories = SoldItem.get_top_categories_with_status(charity_id, 5, "false")

            else:
                # Invalid filter, redirect to all orders
                flash('Invalid filter, redirecting to all orders.')
                return redirect(url_for('order.view_orders', filter='all'))

    fulfilled_count = SoldItem.get_fulfilled_orders_count(charity_id)
    unfulfilled_count = SoldItem.get_unfulfilled_orders_count(charity_id)




    return render_template('seller_orders.html', 
    avail_orders=orders,
    fulfilled_count=fulfilled_count,
    unfulfilled_count=unfulfilled_count,
    mynum=charity_id, 
    charityName=name,
    top_categories = top_categories)


#removes items from seller list
@bp.route('/sells/inventory/remove/<int:product_id>', methods=['POST'])
def sells_remove(product_id):
    #Purchase.add_purchase(current_user.id, product_id, datetime.datetime.now()) #how to get the current time
    SoldItem.remove_charity_item(product_id)
    return redirect(url_for('index.seller_inventory'))

#adds to inventory
@bp.route('/sells/inventory/add/', methods=['POST'])
def sells_add():


    print("reached sells_add method")


    # Retrieving form data:
    name = request.form.get('name', default='', type=str)
    #price = request.form.get('price', default=0.0, type=float)


    starting_bid = request.form.get('startingBid', default=0.0, type=float)
    buy_now = request.form.get('buyNow', default=0.0, type=float)


    category = request.form.get('category', default='', type=str)
    #expiration_str = request.form.get('expiration', default='', type=str)
    image = request.form.get('image', default='', type=str)


    # Retrieve separate expiration date components
    expiration_month_name = request.form.get('expiration_month', default='', type=str)
    expiration_day = request.form.get('expiration_day', default='', type=str)
    expiration_year = request.form.get('expiration_year', default='', type=str)

    # Retrieve expiration time
    expiration_time = request.form.get('expiration_time', default='', type=str)



    # Validate the form data (might remove this if statement altogether??)
    #if not name or not price or not expiration_month_name or not expiration_day or not expiration_year or not expiration_time:
    if not name or not starting_bid or not buy_now or not expiration_month_name or not expiration_day or not expiration_year or not expiration_time:
        flash('Name, price, and expiration details are required fields.', 'error')
        return redirect(url_for('index.seller_inventory'))

    charityId = User.getCharityId(current_user.id)

    if SoldItem.get_charity_items_with_id_name(charityId, name):

        return redirect(url_for('index.seller_inventory'))

    month_name_to_number = {
    'January': '01',
    'February': '02',
    'March': '03',
    'April': '04',
    'May': '05',
    'June': '06',
    'July': '07',
    'August': '08',
    'September': '09',
    'October': '10',
    'November': '11',
    'December': '12'
    }


    # Convert the month name to the corresponding number
    expiration_month = month_name_to_number.get(expiration_month_name)
    if not expiration_month:
        flash('Invalid month name.', 'error')
        return redirect(url_for('index.seller_inventory'))


    # Combine expiration components into a string
    expiration_str = f"{expiration_year}-{expiration_month}-{expiration_day} {expiration_time}"


    #expiration_dt = datetime.strptime(expiration_str, '%Y-%m-%d %H:%M:%S.%f')
    expiration_dt = datetime.datetime.strptime(expiration_str, '%Y-%m-%d %H:%M:%S')




    charityId = User.getCharityId(current_user.id) # TO DO: Need to make sure that this can be cast as an int


    #SoldItem.add_charity_item(charityId, name, price, category, expiration_dt, image)
    SoldItem.add_charity_item(charityId, name, starting_bid, buy_now, category, expiration_dt, image)






    return redirect(url_for('index.seller_inventory'))








