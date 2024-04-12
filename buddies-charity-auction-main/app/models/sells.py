from flask import current_app as app

from collections import Counter

from .product import Product
from .user import User
from .order import Order
from .bid import Bid




class SoldItem:
    def __init__(self, charityId):
        print("charityID is" + str(charityId))
        self.charityId = charityId
    #self.productId = productId


    @staticmethod
    def get_charity_items(charityId): # get ALL items sold by a given charity (by charityId)
        # Original query:
        #SELECT P.id, P.name, P.price, P.available FROM Sells AS S JOIN Products AS P ON S.productId = P.id WHERE S.charityId = :charityId;
        rows = app.db.execute('''
    SELECT P.id, P.name, P.starting_bid, P.buy_now, P.available, P.catergory,P.expiration, P.image, P.rating FROM Sells AS S JOIN Products AS P ON S.productId = P.id WHERE S.charityId = :charityId AND P.available = true;
    ''',
                                charityId=charityId)


        return [Product(*row) for row in rows]

    @staticmethod
    def get_charity_items_with_id_name(charityId, name):
        # Get items sold by a given charity with a specific name
        rows = app.db.execute('''
            SELECT P.id, P.name, P.starting_bid, P.buy_now, P.available, P.catergory, P.expiration, P.image, P.rating
            FROM Sells AS S
            JOIN Products AS P ON S.productId = P.id
            WHERE S.charityId = :charityId AND P.name = :name AND P.available = true;
        ''', charityId=charityId, name=name)

        return [Product(*row) for row in rows]

# get ALL items sold by a given charity (by charityId)
    @staticmethod
    def get_charity_orders(charityId): 
        rows = app.db.execute('''
            SELECT O.id, O.purchaseId, O.productName, O.buyerId, O.sellerId, O.date_placed, O.total_cost, O.status
            FROM Orders AS O
            WHERE O.sellerId = :charityId;
        ''', charityId=charityId)


        return [Order(*row) for row in rows]

# get ALL charity orders from most recent to latest
    @staticmethod
    def get_charity_orders_reverse_chronological(charityId):
        rows = app.db.execute('''
            SELECT O.id, O.purchaseId, O.productName, O.buyerId, O.sellerId, O.date_placed, O.total_cost, O.status
            FROM Orders AS O
            WHERE O.sellerId = :charityId
            ORDER BY O.date_placed DESC;  -- Order by date_placed in descending order
        ''', charityId=charityId)

        return [Order(*row) for row in rows]



# remove item from Sells when purchased
    @staticmethod
    def remove_charity_item(pid):
        try:


            app.db.execute("""
                DELETE FROM Sells WHERE productId = :pid;
            """,
                                    pid = pid)


            print("Deleted from Sells:" + str(pid))
            #TODO: Decide if we need to delete from products??
            # app.db.execute("""
            #     DELETE FROM Products WHERE id = :pid;
            # """,
            #                         pid = pid)
            # print("Deleted from Products:" + str(pid))


            #Revision: set available attribute for product in Products table ==> to False
                        # Set available attribute to False for the product in Products table

            
            app.db.execute("""
                UPDATE Products
                SET available = FALSE
                WHERE id = :pid;
            """, pid=pid)




            # JUST FOR TESTING
            rows = app.db.execute("""
                SELECT available
                FROM Products
                WHERE id = :pid;
            """, pid=pid)
            
            print("this is updated product availability")
            print(rows[0][0])
            # END OF TESTSING


            print("Updated availability of just sold item to FALSE in the Products table.")




            #id = rows[0][0]
            #return Purchase.get(id)
        except Exception as e:
            print("Exception in remove_charity_item reached")

            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None



# add item to charity's inventory
    @staticmethod
    def add_charity_item(charityId, name, starting_bid, buy_now, category, expiration, image):


        #charityId, name, starting_bid, buy_now, category, expiration_dt, image
        #try:
        # Step 1: Add a new product to the Products table


        # result = app.db.execute("""
        #     INSERT INTO Products (name, price)
        #     VALUES (:name, :price)
        #     RETURNING id;
        # """, name=name, price=price)
                # Step 1: Add a new product to the Products table
        result = app.db.execute("""
            INSERT INTO Products (name, starting_bid, buy_now, available, catergory, expiration, image, rating)
            VALUES (:name, :starting_bid, :buy_now, TRUE, :category, :expiration, :image, 0.0)
            RETURNING id;
        """, name=name, starting_bid=starting_bid, buy_now = buy_now, category=category, expiration=expiration, image=image)
        


        product_id = result[0][0]


        #expiration_test = result[0][5]
        # print("expiration:")
        #print(expiration_test)
        ##print(type(expiration_test))
        #product_id = result.fetchone()[0]
        #print(product_id)
        #print(type(product_id))
        


        # Step 2: Associate the product with the charity in the Sells table
        app.db.execute("""
            INSERT INTO Sells (charityId, productId)
            VALUES (:charityId, :productId);
        """, charityId=charityId, productId=product_id)


        return 4
        # except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            #print(str(e))
            #return None



    # update availability of product.
    @staticmethod
    def update_available(product_id, new_status): # for example, new_status = False or new_status = True
        try:
            app.db.execute("""
                UPDATE Products
                SET available = :new_status
                WHERE id = :product_id;
            """, new_status=new_status, product_id=product_id)


            print(f"Product {product_id} availability updated to {new_status}")
        except Exception as e:
            print(f"Error updating product availability: {str(e)}")


    def search_by_seller(search_query): # TODO: CHANGE THISSSSS
        rows = app.db.execute('''
        SELECT P.*
        FROM Products P
        JOIN Sells S ON P.id = S.productId
        JOIN Charities C ON S.charityId = C.id
        WHERE LOWER(C.name) LIKE LOWER(:name)
    ''', name='%'+search_query+'%')
        return [Product(*row) for row in rows]

 # get all fulfilled orders and their count
    @staticmethod
    def get_fulfilled_orders_count(charityId):
        rows = app.db.execute('''
            SELECT COUNT(*) 
            FROM Orders AS O
            WHERE O.sellerId = :charityId AND O.status = TRUE;
        ''', charityId=charityId)

        return rows[0][0] if rows else 0

 # get all unfulfilled orders and their count
    @staticmethod
    def get_unfulfilled_orders_count(charityId):
        rows = app.db.execute('''
            SELECT COUNT(*) 
            FROM Orders AS O
            WHERE O.sellerId = :charityId AND O.status = FALSE;
        ''', charityId=charityId)

        return rows[0][0] if rows else 0

    # return top N categories given charity ID and an integer
    @staticmethod
    def get_top_categories(charityId, top_n):
        rows = app.db.execute('''
            SELECT P.catergory, COUNT(*) as order_count
            FROM Orders AS O
            JOIN Products AS P ON O.productName = P.name
            WHERE O.sellerId = :charityId
            GROUP BY P.catergory
            ORDER BY order_count DESC
            LIMIT :top_n;
        ''', charityId=charityId, top_n=top_n)


        # Format the result into a list of dictionaries
        top_categories = [{'category': row[0], 'order_count': row[1]} for row in rows]



        return top_categories

    # return top N categories given charity ID and an integer
    @staticmethod
    def get_top_categories_with_status(charityId, top_n, status):
        rows = app.db.execute('''
            SELECT P.catergory, COUNT(*) as order_count
            FROM Orders AS O
            JOIN Products AS P ON O.productName = P.name
            WHERE O.sellerId = :charityId AND O.status = :status
            GROUP BY P.catergory
            ORDER BY order_count DESC
            LIMIT :top_n;
        ''', charityId=charityId, top_n=top_n, status=status)


        # Format the result into a list of dictionaries
        top_categories = [{'category': row[0], 'order_count': row[1]} for row in rows]



        return top_categories

    # get N top rated items based on charity (charity Id)
    @staticmethod
    def get_top_rated_items(charityId, top_n):
        rows = app.db.execute('''
            SELECT P.id, P.name, P.starting_bid, P.buy_now, P.available, P.catergory, P.expiration, P.image, P.rating
            FROM Sells AS S
            JOIN Products AS P ON S.productId = P.id
            WHERE S.charityId = :charityId AND P.available = true
            ORDER BY P.rating DESC
            LIMIT :top_n;
        ''', charityId=charityId, top_n=top_n)

        return [Product(*row) for row in rows]


    # get N top rated items based on charity (charity Id) less than or equal to $50
    @staticmethod
    def get_top_rated_items_less_than_fifty(charityId, top_n):
        rows = app.db.execute('''
            SELECT P.id, P.name, P.starting_bid, P.buy_now, P.available, P.catergory, P.expiration, P.image, P.rating
            FROM Sells AS S
            JOIN Products AS P ON S.productId = P.id
            WHERE S.charityId = :charityId AND P.available = true AND P.buy_now <= 50
            ORDER BY P.rating DESC
            LIMIT :top_n;
        ''', charityId=charityId, top_n=top_n)

        return [Product(*row) for row in rows]


    # get N top rated items based on charity (charity Id) greater than $50
    @staticmethod
    def get_top_rated_items_greater_than_fifty(charityId, top_n):
        rows = app.db.execute('''
            SELECT P.id, P.name, P.starting_bid, P.buy_now, P.available, P.catergory, P.expiration, P.image, P.rating
            FROM Sells AS S
            JOIN Products AS P ON S.productId = P.id
            WHERE S.charityId = :charityId AND P.available = true AND P.buy_now > 50
            ORDER BY P.rating DESC
            LIMIT :top_n;
        ''', charityId=charityId, top_n=top_n)

        return [Product(*row) for row in rows]


    # get top N earliest to expire items sold by specific charity (charityId)
    @staticmethod
    def get_earliest_expiring_items(charityId, limit=5):
        rows = app.db.execute('''
            SELECT P.id, P.name, P.starting_bid, P.buy_now, P.available, P.catergory, P.expiration, P.image, P.rating
            FROM Sells AS S
            JOIN Products AS P ON S.productId = P.id
            WHERE S.charityId = :charityId AND P.available = true
            ORDER BY P.expiration ASC
            LIMIT :limit;  -- Limit the results to the specified number (default is 5)
        ''', charityId=charityId, limit=limit)

        return [Product(*row) for row in rows]


    # get top N earliest to expire items sold by specific charity (charityId) UNDER $50
    @staticmethod
    def get_earliest_expiring_items_under_fifty(charityId, limit=5):
        rows = app.db.execute('''
            SELECT P.id, P.name, P.starting_bid, P.buy_now, P.available, P.catergory, P.expiration, P.image, P.rating
            FROM Sells AS S
            JOIN Products AS P ON S.productId = P.id
            WHERE S.charityId = :charityId AND P.available = true AND P.buy_now <= 50
            ORDER BY P.expiration ASC
            LIMIT :limit;  -- Limit the results to the specified number (default is 5)
        ''', charityId=charityId, limit=limit)

        return [Product(*row) for row in rows]

    # get top N earliest to expire items sold by specific charity (charityId) OVER $50
    @staticmethod
    def get_earliest_expiring_items_over_fifty(charityId, limit=5):
        rows = app.db.execute('''
            SELECT P.id, P.name, P.starting_bid, P.buy_now, P.available, P.catergory, P.expiration, P.image, P.rating
            FROM Sells AS S
            JOIN Products AS P ON S.productId = P.id
            WHERE S.charityId = :charityId AND P.available = true AND P.buy_now > 50
            ORDER BY P.expiration ASC
            LIMIT :limit;  -- Limit the results to the specified number (default is 5)
        ''', charityId=charityId, limit=limit)

        return [Product(*row) for row in rows]


