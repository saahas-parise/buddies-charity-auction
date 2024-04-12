from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class Charity(UserMixin):
    def __init__(self, id, orgId, name, email, password):
        self.id = id
        self.orgId = orgId
        self.name = name
        self.email = email
        self.password = password

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, name
FROM Charities
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Charities
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, name):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, name)
VALUES(:email, :password, :name)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  name=name)
            id = rows[0][0]
            return User.get(id) # TODO
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None


    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, name
FROM Charities
WHERE id = :id
""",
                              id=id)
        return Charity(*(rows[0])) if rows else None

    @staticmethod
    def get_charity_id_by_user_id(user_id):
        rows = app.db.execute('''
            SELECT id
            FROM Charities
            WHERE userid = :user_id
        ''', user_id=user_id)
        return rows[0][0] if rows else None

    #fethches threads where the charity is involved
    @staticmethod
    def get_message_threads(charity_id):

        threads = app.db.execute('''
            SELECT mt.id, mt.subject, p.name, u.firstname || ' ' || u.lastname as user_name
            FROM MessageThreads mt
            JOIN Products p ON mt.product_id = p.id
            JOIN Sells s ON p.id = s.productId
            JOIN Users u ON s.charityId = u.id
            WHERE s.charityId = :charity_id
        ''', charity_id=charity_id)
        return threads
    #fethces messages for a given thread
    @staticmethod
    def get_messages_for_thread(thread_id):
        
        messages = app.db.execute('''
            SELECT m.*, u.firstname || ' ' || u.lastname as sender_name
            FROM Messages m
            JOIN Users u ON m.sender_id = u.id
            WHERE m.thread_id = :thread_id
            ORDER BY m.time_sent
        ''', thread_id=thread_id)
        return messages