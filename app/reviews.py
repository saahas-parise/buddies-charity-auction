from flask import render_template, request, abort
from flask import redirect, url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import ValidationError, InputRequired, Email, EqualTo
import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.review import ProductReview

from flask import Blueprint
from flask import jsonify
bp = Blueprint('reviews', __name__)


#Form for finding 5 most recent reviews
class findReview(FlaskForm):
    user_id = IntegerField('User_ID', validators=[InputRequired('Please enter a user id!')])
    submit = SubmitField('Find 5 most recent reviews!')

#index page for reviews that shows user reviews with update/delete functionality
@bp.route('/reviews', methods=['POST', 'GET'])
def index():
    page = int(request.args.get('page', default=1))

    form = findReview()
    if form.validate_on_submit():
        uid = form.user_id.data
        return redirect('reviews/'+str(uid))
    elif request.method == 'POST':
        if request.form['action'] == 'delete_review':
            ProductReview.delete_by_id(request.form['review_id'])
            reviews = ProductReview.get_all()
            myReviews = ProductReview.get_by_uid(current_user.id)
            return render_template('reviews.html', all_reviews=reviews, my_reviews=myReviews, form=form, page=page)
    if current_user.is_authenticated:
        reviews = ProductReview.get_all()
        myReviews = ProductReview.get_by_uid(current_user.id)
        return render_template('reviews.html', all_reviews=reviews, my_reviews=myReviews, form=form, page=page)
    else:
        reviews = ProductReview.get_all()
        return render_template('reviews.html', all_reviews=reviews, form=form, page=page)

#getting reviews for a specific user
@bp.route('/reviews/<int:uid>', methods=['POST', 'GET'])
def fiveRecent(uid):
    if current_user.is_authenticated:
        reviewsbysoso = ProductReview.get_5_most_recent(uid)
        myReviews = ProductReview.get_by_uid(current_user.id)
        reviews = ProductReview.get_all()
        return render_template('5reviews.html', soso_reviews=reviewsbysoso,all_reviews=reviews, my_reviews=myReviews)
    else:
        reviewsbysoso = ProductReview.get_5_most_recent(uid)
        reviews = ProductReview.get_all()
        return render_template('5reviews.html', soso_reviews=reviewsbysoso,all_reviews=reviews)
        

#page for adding reviews
@bp.route('/addReview', methods=['GET', 'POST'])
def addReview():
    if not current_user.is_authenticated:
        return redirect(url_for('index.index'))

    pid = request.args.get('id')
    my_review = ProductReview.get_last_review(pid, current_user.id)

    # Handle the post request
    if request.method == 'POST':
        now = datetime.datetime.now()
        ProductReview.add_review(current_user.id, pid, request.form['rating'], now, request.form['comment'])
        
        return redirect('product/'+str(pid))
    return render_template('addOrUpdateReview.html', my_review=my_review, isNewReview=my_review is None)
