from functools import wraps
from flask import session , redirect , url_for , jsonify
from auth_queries import get_user_session_token, update_user_heartbeat


def login_required(f):
    @wraps(f)
    def decorated_function(*args , **kwargs):
        if 'username' not in session:
            return redirect(url_for('home'))

        db_token = get_user_session_token(session['username'])
        client_token = session.get('session_token')

        if not db_token or db_token!=client_token:
            session.pop('username',None)
            session.pop('session_token',None)
            return redirect(url_for('home'))
        update_user_heartbeat(session['username'])
        return f(*args, **kwargs)

      
    return decorated_function

    
def api_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'success': False, 'error': 'Unauthorized. Please login first.'}), 401

        db_token = get_user_session_token(session['username'])
        client_token = session.get('session_token')
        if not db_token or db_token != client_token:
            session.pop('username', None)
            session.pop('session_token', None)
            return jsonify({'success': False, 'error': 'Session expired or logged in elsewhere. Please login again.'}), 401
            
        update_user_heartbeat(session['username'])
        return f(*args, **kwargs)
    return decorated_function
