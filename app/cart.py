from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from .models.cart import Cart

bp = Blueprint('cart', __name__)

#gets what's currently in the authenticated users cart/wishlist
@bp.route('/cart', methods=['POST', 'GET'])
def cart():
    if current_user.is_authenticated:
        message = None
        already_in_cart = False

        if request.method == 'POST':
            action = request.form.get('action', type=str)
            product_id = request.form.get('product_id', type=int)

            if action == 'add':
                message, already_in_cart = Cart.add_to_cart(current_user.id, product_id)
            elif action == 'remove':
                Cart.remove_from_cart(current_user.id, product_id)

        _cart = Cart.get_cart_for_user(current_user.id)
        total_price = sum(item.product_price for item in _cart) if _cart else 0
        return render_template('cart.html', cart=_cart, total_price=total_price, message=message, already_in_cart=already_in_cart)

    else:
        flash("You must be logged in to view the cart.")
        return redirect(url_for('users.login'))

#favorite goes to the top
@bp.route('/toggle_favorite/<int:product_id>', methods=['POST'])
@login_required
def toggle_favorite(product_id):
    result = Cart.toggle_favorite(current_user.id, product_id)
    flash(result)
    return redirect(url_for('cart.cart'))

@bp.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    product_id = request.form.get('product_id', type=int)
    Cart.remove_from_cart(current_user.id, product_id)
    return redirect(url_for('cart.cart'))
# initiates thread and sends message
@bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    product_id = request.form.get('product_id', type=int)
    message = request.form.get('message', type=str)
    seller_id = request.form.get('seller_id', type=int) 

   
    subject = f"Message regarding price of product {product_id}"

    thread_id = Cart.initiate_message_thread(product_id, current_user.id, seller_id, subject)
    Cart.send_message(thread_id, current_user.id, seller_id, message)

    flash('Message sent successfully.')
    return redirect(url_for('cart.cart'))

@bp.route('/messages/<int:thread_id>')
@login_required
def view_messages(thread_id):
    try:
        messages = Cart.get_messages_for_thread(thread_id)
        return render_template('view_messages.html', messages=messages, thread_id=thread_id)
    except AttributeError as e:
        print("The method get_messages_for_thread is not defined:", e)


@bp.route('/reply_to_thread/<int:thread_id>', methods=['POST'])
@login_required
#gets message from the form
def reply_to_thread(thread_id):
    reply_message = request.form.get('reply_message')
    flash('Reply sent successfully.')
    return redirect(url_for('cart.view_messages', thread_id=thread_id))


@bp.route('/reply_to_message/<int:message_id>', methods=['POST'])
@login_required
def reply_to_message(message_id):
    reply_content = request.form.get('reply', '')
    if not reply_content:
        flash('Your reply cannot be empty.', 'error')
        return redirect(url_for('cart.view_messages', thread_id=message_id))
    try:
        Cart.reply_to_message(message_id, current_user.id, reply_content)
        flash('Your reply has been sent.', 'success')
    except Exception as e:
        flash('An error occurred while sending your reply.', 'error')
        app.logger.error(f'Error replying to message: {e}')
    return redirect(url_for('cart.view_messages', thread_id=message_id))
