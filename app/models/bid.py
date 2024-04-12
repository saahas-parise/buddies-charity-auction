from flask import current_app as app
from flask_login import current_user

class Bid:
    #def __init__(self, bidID, uid, pid, amount, bidtime): #!!!Added Name
    def __init__(self, bidID, uid, pid, amount, bidtime): 
        self.uid = uid
        self.id = bidID
        self.pid = pid
        self.amount = amount
        self.bidtime= bidtime
        self.product_name = Bid.get_product_name(pid)
        

    @staticmethod
    #returns bid with matching bidID
    def get(id):
        rows = app.db.execute('''
SELECT *
FROM Bids
WHERE id = :id
''',
                              id=id)
        return Bid(*(rows[0])) if rows else None
    
    #retuns a user's list of bids
    @staticmethod
    def get_bids(uid): 
        rows = app.db.execute('''
SELECT Bids.id, Bids.uid, Bids.pid, Bids.amount, Bids.bidtime
FROM Bids, Products
WHERE uid = :uid and bids.pid = Products.id
ORDER BY bidtime DESC
''',
                              uid=uid)
        return [Bid(*row) for row in rows]
    
    #returns the single bid with the highest price
    @staticmethod
    def get_max_bid(id):
        rows = app.db.execute('''
SELECT *
FROM Bids AS B
WHERE B.pid = :id
ORDER BY B.amount DESC
LIMIT 1;
''',
                              id=id)
        return Bid(*(rows[0])) if rows else None


    #adds a bid to the bid table
    @staticmethod
    def add_bid(uid, pid, amount, bidtime):
            rows = app.db.execute('''
                    INSERT INTO Bids(uid, pid, amount, bidtime)
                    VALUES(:uid, :pid, :amount, :bidtime)
                    ''', uid=uid,
                                pid=pid,
                                amount=amount, bidtime = bidtime
                                )
            rows = app.db.execute("""
UPDATE Users
SET balance = balance - (SELECT max(amount) FROM Bids WHERE pid = :pid)
WHERE id = :uid
""",
                                  uid=uid,
                                  pid=pid,
                                  )
            return uid

    @staticmethod
    def get_product_name(pid):
        rows = app.db.execute('''
            SELECT name
            FROM Products
            WHERE id = :pid
        ''', pid=pid)
        return rows[0][0] if rows else None