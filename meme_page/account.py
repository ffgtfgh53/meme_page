"""For the routes associated with the user
E.g. /account and /bookmarks"""

from flask import Blueprint, render_template
from flask_login import current_user, login_required

account = Blueprint('account', __name__)

@account.route('/profile')
@login_required
def profile():
    return render_template('account/profile.html')