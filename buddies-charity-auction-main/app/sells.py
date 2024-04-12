


# from flask import jsonify, url_for, redirect, render_template
# from flask_login import current_user
# import datetime
# from humanize import naturaltime

# from .models.sells import SoldItem

"""
@bp.route('/wishlist')
def wishlist():
    if current_user.is_authenticated:
        items = WishlistItem.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
        return render_template('wishlist.html',
                               items=items,
                               humanize_time=humanize_time)
    else:
        return jsonify({}), 404
"""

#'/sells/<int:charityId>

# @bp.route('/sells/', methods = ['GET', 'POST'])
# def sells():

#     print("in function")
    
#     items = SoldItem.get_charity_items(charityId)
#     print(items)

#     return render_template('index.html')

        
#         #return render_template('soldItems.html',
#                                 #items=items,
#                                # humanize_time=humanize_time)
#        # else len(items) == 0:
#             #return jsonify({}), 404



