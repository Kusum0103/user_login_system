from flask import Flask, render_template , request, jsonify, session, redirect, url_for
import mysql.connector
import os
from database import get_db_connection
from auth import is_valid_email, check_password_strength,check_username_exists, register_user, verify_user_login

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    if not username or not email or not password or not confirm_password :
        return jsonify({'success' : False, 'error': "All fields are required."}), 400
    if not is_valid_email(email):
        return jsonify({'success' : False, 'error': "Invalid Email Address."}), 400

    is_strong,password_strength_message = check_password_strength(password)
    if not is_strong:
        return jsonify({'success' : False, 'error': password_strength_message}), 400

    if password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match.'}), 400

    
    