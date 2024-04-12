from flask import current_app as app
from flask import jsonify
import datetime
from humanize import naturaltime
from .bid import Bid


class Product:


    # buyNow to getbuyNow()
    # product.price is supposed to be bid price????? NOT the buy now price
    # charity must be able to set BOTH buy now price AND bid price


    #add purchase
    def __init__(self, id, name, starting_bid, buy_now, available, catergory, expiration, image, rating):
        self.id = id
        self.name = name
        #self.price = Bid.get_max_bid(id).amount if Bid.get_max_bid(id) else price#Price is instantiated as current bid amount
        self.starting_bid = starting_bid
        self.buy_now = buy_now
        self.available = available
        self.image = image
        self.catergory = catergory
        #self.expiration = expiration
        self.expiration = naturaltime(datetime.datetime.now() - expiration)
        #print("successfully set self.expiration.\n")
        self.rating = rating

        self.current_max_bid = Bid.get_max_bid(id).amount if Bid.get_max_bid(id) else starting_bid


    @staticmethod
    def get(id):
        rows = app.db.execute('''
    SELECT id, name, starting_bid, buy_now, available, catergory, expiration, image, rating
    FROM Products
    WHERE id = :id
    ''',
                                id=id)
        return Product(*(rows[0])) if rows is not None else None
    #gets all available products
    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
    SELECT id, name, starting_bid, buy_now, available, catergory, expiration, image, rating
    FROM Products
    WHERE available = :available
                                AND expiration >= now()
    ''',
                                available=available)
        return [Product(*row) for row in rows]

    # new method: get all available products such that they are not purchased.
    @staticmethod
    def get_available_and_not_purchased():
        rows = app.db.execute('''
            SELECT id, name, starting_bid, buy_now, available, catergory, expiration, image, rating
            FROM Products
            WHERE available = true
            AND expiration >= now()
            AND id NOT IN (SELECT pid FROM Purchases)
        ''')

        return [Product(*row) for row in rows]
    
    #gets all available products within the given category
    @staticmethod
    def get_all_by_category(catergory, available):
        rows = app.db.execute('''
    SELECT *
    FROM Products
    WHERE catergory = :catergory
                                AND available = :available


    ''',
                                available=available, catergory =catergory)
        return [Product(*row) for row in rows]




    #     @staticmethod
    #     def getPrice(id):
    #         rows = app.db.execute('''
    # SELECT price
    # FROM Products
    # WHERE id = :id
    # ''',
    #                               id=id)
    #         return int(*(rows[0])) if rows else None


    
    
    #returns the price of the product
    @staticmethod
    def getBuyNow(id):
        rows = app.db.execute('''
    SELECT buy_now
    FROM Products
    WHERE id = :id
    ''',
                                id=id)
        return int(*(rows[0])) if rows else None
    
    #returns the category of the product given the id
    @staticmethod
    def getCategory(id):
        rows = app.db.execute('''
    SELECT catergory
    FROM Products
    WHERE id = :id
    ''',
                                id=id)
        return int(*(rows[0])) if rows else None

    # return category given product name
    @staticmethod
    def get_category_by_name(product_name):
        # Query to get the category based on the product name
        rows = app.db.execute('''
            SELECT catergory
            FROM Products
            WHERE name = :product_name;
        ''', product_name=product_name)

        # Check if any result is found
        if rows:
            return rows[0][0]  # Return the category
        else:
            return None
    
    #returns the product's seller
    @staticmethod
    def get_seller(id):
        row = app.db.execute('''
        SELECT charityId
        FROM Sells
        WHERE productId = :id
    ''', id=id).fetchone()
        return Product(*(row)) if row is not None else None

    #returns the most expensive product
    def get_most_expensive():
        rows = app.db.execute('''
    SELECT * FROM Products
                                WHERE expiration >= now()
                                AND available = :available
    ORDER BY buy_now DESC
                            
                            
    ''',
    available = True)
        return [Product(*row) for row in rows]
    
    #returns the product with a matching name
    def search_by_name(search_query):
        rows = app.db.execute('''
    SELECT *
    FROM Products
    WHERE LOWER(name) LIKE LOWER(:name)
                                AND available = true
                                AND expiration >= now()
    ''', name='%'+search_query+'%')
        return [Product(*row) for row in rows]
    
    #returns the least expensive product
    def get_least_expensive():
        rows = app.db.execute('''
    SELECT * FROM Products
                                WHERE expiration >= now()
                                AND available = true
    ORDER BY buy_now
    ''')
        return [Product(*row) for row in rows]
    
    #returns the highest rated product
    def get_highest_rating():
        rows = app.db.execute('''
    SELECT * FROM Products
                                WHERE expiration >= now()
    ORDER BY rating DESC
    ''')
        return [Product(*row) for row in rows]
    
    #returns the expiration date of the product
    def get_expiration():
        rows = app.db.execute('''
    SELECT * FROM Products
    WHERE expiration >= now()
    ORDER BY expiration;
    ''')
        return [Product(*row) for row in rows]







    # TODO: Determine if change_price needs to be modified or just removed ==> AFTER modifying products.py
    #mutator for the price attribute of the product
    @staticmethod
    def change_price(id, amount):
            print('MY ID:' + str(id))
            print('MY AMOUNT:' + str(amount))
            rows = app.db.execute('''
                    UPDATE Products
    SET price = :amount
    WHERE id = :id; ''', id=id,
    amount=amount
                                )
            return id
