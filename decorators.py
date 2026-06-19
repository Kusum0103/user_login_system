from functools import wraps
from flask import session , redirect , url_for , jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args , **kwargs):
        if 'username' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

    
def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized. Please login first.'}), 401
        return f(*args, **kwargs)
    return decorated_function
