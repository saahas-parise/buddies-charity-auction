from flask import current_app as app
from humanize import naturaltime
import datetime


class ProductReview:
    def __init__(self, id, uid, pid, rating, date_posted, feedback, upvote):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.rating = rating
        self.date_posted = naturaltime(datetime.datetime.now() - date_posted)
        self.feedback = feedback
        self.upvote = upvote

    #gets all reviews
    @staticmethod
    def get_all():
        rows = app.db.execute('''
                                SELECT id, uid, pid, rating, date_posted, feedback, upvote
                                FROM Reviews
                                ORDER BY date_posted DESC
                                ''')
        return [ProductReview(*row) for row in rows]
    
    #gets a review based on unique review id
    @staticmethod
    def get(id):
        rows = app.db.execute('''
                                SELECT id, uid, pid, rating, date_posted, feedback, upvote
                                FROM Reviews
                                WHERE id = :id
                                ''',id=id)
        return [ProductReview(*row) for row in rows]

    #gets all reviews by a given user
    @staticmethod
    def get_by_uid(uid):
        rows = app.db.execute('''
                                SELECT id, uid, pid, rating, date_posted, feedback, upvote
                                FROM Reviews
                                WHERE uid = :uid
                                ORDER BY upvote DESC, date_posted DESC
                                ''',uid=uid)
        return [ProductReview(*row) for row in rows]
    
    #gets all reviews for a given product
    @staticmethod
    def get_by_pid(pid):
        rows = app.db.execute('''
                                SELECT id, uid, pid, rating, date_posted, feedback, upvote
                                FROM Reviews
                                WHERE pid = :pid
                                ORDER BY upvote DESC, rating DESC
                                ''',pid=pid)
        return [ProductReview(*row) for row in rows]
    
    #get total number of reviews for a given product
    @staticmethod
    def get_total_number_by_id(pid):
        rows = app.db.execute('''
                                SELECT id, uid, pid, rating, date_posted, feedback, upvote
                                FROM Reviews
                                WHERE pid = :pid
                                ORDER BY upvote DESC, rating DESC
                                ''',pid=pid)
        return [] if len(rows) == 0 else len(rows)
    
    #get average rating for a given product
    @staticmethod
    def get_average_rating(pid):
        rows = app.db.execute('''
                                SELECT CAST(AVG(rating) AS INTEGER) AS average_rating
                                FROM Reviews
                                WHERE pid = :pid
                                ''',pid=pid)
        return rows[0][0] if rows else None


    #finds 5 most recent reviews for a given user
    @staticmethod
    def get_5_most_recent(uid):
        rows = app.db.execute('''
                                SELECT id, uid, pid, rating, date_posted, feedback, upvote
                                FROM Reviews
                                WHERE uid = :uid
                                ORDER BY upvote DESC, date_posted DESC
                                LIMIT 5
                                ''', uid=uid)
        return [ProductReview(*row) for row in rows]

    #delete reviews
    @staticmethod
    def delete_by_id(id):
        rows = app.db.execute('''
                            DELETE FROM Reviews
                            WHERE id = :id; ''',id=id)
        return None
    
    #add review
    @staticmethod
    def add_review(uid, pid, rating, date_posted, feedback):
        rows = app.db.execute('''
                INSERT INTO Reviews(uid, pid, rating, date_posted, feedback)
                VALUES(:uid, :pid, :rating, :date_posted, :feedback)
                ON CONFLICT (uid, pid) DO UPDATE 
                SET rating = :rating,
                    date_posted = :date_posted,
                    feedback = :feedback
                RETURNING id; ''', uid=uid,
                              pid=pid,
                              rating=rating,
                              date_posted=date_posted,
                              feedback=feedback)
        id = rows[0][0]
        return id
    
    #get last review
    @staticmethod
    def get_last_review(pid, uid):
        rows = app.db.execute('''
                SELECT id, uid, pid, rating, date_posted, feedback, upvote
                FROM Reviews
                WHERE pid = :pid AND uid = :uid
            ''', pid=pid, uid=uid)
        return None if rows is None or len(rows) == 0 else ProductReview(*(rows[0]))
    
    #update upvote
    @staticmethod
    def update_upvote_for_id(review_id: int, offset: int, uid: int):
        rows = app.db.execute('''
                        INSERT INTO Reviewtransactions
                        VALUES ((select nextval('reviewtransactions_id_seq')),:review_id,:uid,current_timestamp, :offset)
                        ON CONFLICT (review_id,uid) DO UPDATE 
                        SET time_upvoted = current_timestamp , 
                              amount = :offset;
                        ''',
                              review_id=review_id,
                              offset=offset,
                              uid=uid,
                              )
        return None
    
    def isVoted(self, uid: int):
        rows = app.db.execute('''
                        SELECT amount 
                        FROM Reviewtransactions
                        WHERE review_id = :id
                        AND uid = :uid
                        ''', uid=uid,
                              id=self.id)
        print(0 if len(rows) == 0 else int(rows[0][0]))
        return 0 if len(rows) == 0 else int(rows[0][0])
