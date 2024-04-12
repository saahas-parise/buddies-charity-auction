from flask import current_app as app
import datetime
from .. import login
from .product import Product
from .user import User

class Cart:
    def __init__(self, product_id, product_name, buyer_id, product_price, seller_id, is_favorite):
        self.product_id = product_id
        print(product_id)
        self.product_name = product_name
        self.buyer_id = buyer_id
        self.product_price = product_price
        self.seller_id = seller_id
        self.is_favorite = is_favorite

        print("seller_id of Cart object:")
        print(seller_id)

        self.seller_name = User.getCharityNameGivenCharityId(seller_id)

    # gets what's currently in a given user's cart
    @staticmethod
    def toggle_favorite(buyer_id, product_id):
        row = app.db.execute('''
        SELECT is_favorite FROM Cart WHERE buyer_id=:buyer_id AND product_id=:product_id;
        ''', buyer_id=buyer_id, product_id=product_id)

        if row:
            new_status = not row[0][0]
            app.db.execute('''
            UPDATE Cart SET is_favorite=:new_status WHERE buyer_id=:buyer_id AND product_id=:product_id;
            ''', new_status=new_status, buyer_id=buyer_id, product_id=product_id)
            return " "
        else:
            return "Item not found in cart."

    
    #gets what's currently in a given users cart
    # can get to buy now from the wishlist!
    @staticmethod
    def get_cart_for_user(buyer_id): 
    # Ensure the SELECT statement fetches all fields required for Cart initialization
        rows = app.db.execute('''
        SELECT Cart.product_id, Products.name, Cart.buyer_id, Products.buy_now As product_price, Sells.charityId As seller_id, Cart.is_favorite
        FROM Cart
        JOIN Products ON Cart.product_id = Products.id
        LEFT JOIN Sells ON Products.id = Sells.productId
        WHERE Cart.buyer_id = :buyer_id
        ORDER BY Cart.is_favorite DESC, Cart.product_id
        ''', buyer_id=buyer_id)
        return [Cart(*row) for row in rows]

    # adds a product to a user's cart for a given user id and product id
    @staticmethod
    def add_to_cart(buy_id, product_id):
        print(f"Attempting to add product {product_id} to cart for user {buy_id}")
        rows = app.db.execute('''
        SELECT * FROM Cart WHERE buyer_id=:buy_id AND product_id=:product_id;
        ''', buy_id=buy_id, product_id=product_id)
        print(f"Product already in cart check returned: {rows}")
        if len(rows) == 0:
            app.db.execute('''
            INSERT INTO Cart(product_id, buyer_id)
            VALUES (:product_id, :buy_id);
            ''', product_id=product_id, buy_id=buy_id)
            return "Product added to cart.", False
        else:
            print(f"Product {product_id} is already in the cart for user {buy_id}")
            return "Product already in the cart.", True

    # removes a product from a user's cart for a given product and user id
    @staticmethod
    def remove_from_cart(buyer_id, product_id):
        rows = app.db.execute('''
        DELETE FROM Cart WHERE buyer_id=:buy_id AND Cart.product_id=:product_id;
        ''', buy_id=buyer_id, product_id=product_id)
        return rows
    #initiates a message thread and checks if a thread already exists

    @staticmethod
    def initiate_message_thread(product_id, buyer_id, seller_id, subject):
        existing_thread = app.db.execute('''
            SELECT id FROM MessageThreads
            WHERE product_id=:product_id
        ''', product_id=product_id)

        if existing_thread:
            return existing_thread[0][0] 

  
        new_thread_id = app.db.execute('''
            INSERT INTO MessageThreads(product_id, subject)
            VALUES (:product_id, :subject)
            RETURNING id
        ''', product_id=product_id, subject=subject)
        return new_thread_id[0][0]

    #allows sending of messages
    @staticmethod
    def send_message(thread_id, sender_id, receiver_id, message):
        app.db.execute('''
            INSERT INTO Messages(thread_id, sender_id, receiver_id, message)
            VALUES (:thread_id, :sender_id, :receiver_id, :message)
        ''', thread_id=thread_id, sender_id=sender_id, receiver_id=receiver_id, message=message)
    
    #gets the messages for the message thread
    @staticmethod
    def get_messages_for_thread(thread_id):
        try:
            rows = app.db.execute('''
            SELECT m.*, u.firstname || ' ' || u.lastname as sender_name
            FROM Messages m
            JOIN Users u ON m.sender_id = u.id
            WHERE m.thread_id = :thread_id
            ORDER BY m.time_sent
            ''', thread_id=thread_id)
            return rows
        except Exception as e:
            print("An error occurred while retrieving messages for thread:", e)
            return []
