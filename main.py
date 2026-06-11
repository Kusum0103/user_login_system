from flask import Flask, render_template , request, jsonify, session, redirect, url_for
import mysql.connector
import os
import json
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


    db = get_db_connection()
    if not db:
        return jsonify({'success': False, 'error': 'Database connection failed.'}), 500
    try:
        cursor = db.cursor()
        if check_username_exists(cursor, username):
            return jsonify({'success' : False, 'error': "Username already exists."}), 400
        
        register_user(db, cursor, username, email, password)
        return jsonify({'success': True, 'message': 'Registration Successfull! You can Login Now'})
    except mysql.connector.Error as e:
        return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        db.close()
    
@app.route('/login',methods = ['POST'])
def login():
    username = request.form.get('username','').strip()
    password = request.form.get('password','')
    
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and Password are required.'}), 400
    
    db = get_db_connection()
    if not db:
        return jsonify({'success': False, 'error': 'Database connection failed.'}), 500
    try:
        cursor = db.cursor()
        success, message = verify_user_login(cursor, username, password)
        if success:
            session['username'] = username
            cursor.execute("SELECT id FROM users WHERE username = %s",(username,))
            user_id = cursor.fetchone()[0]
            cursor.execute("UPDATE users SET is_active = 1 WHERE id = %s ", (user_id,))


            user_agent = request.headers.get('User-Agent', 'Unknown')

            print(json.dumps(dict(request.headers), indent=4))



            if 'Windows' in user_agent:
                os_name = 'Windows'
            elif 'Mac' in user_agent:
                os_name = 'macOS'
            elif 'Linux' in user_agent:
                os_name = 'Linux'
            elif 'Android' in user_agent:
                os_name = 'Android'
            elif 'iPhone' in user_agent:
                os_name = 'iPhone'
            else:
                os_name = 'Unknown OS'
            if 'Edge' in user_agent:
                browser = 'Edge'
            elif 'Chrome' in user_agent:
                browser = 'Chrome'
            elif 'Firefox' in user_agent:
                browser = 'Firefox'
            elif 'Safari' in user_agent:
                browser = 'Safari'
            else:
                browser = 'Browser'
            
            device_info = f"{browser} on {os_name}"
            
            cursor.execute(
                "INSERT INTO login_logs (user_id, device_info) VALUES (%s, %s)",
                (user_id, device_info)
            )


            db.commit()
            return jsonify({'success': True, 'message': message })
        else:
            return jsonify({'success' : False , 'error' : message}), 401
     
    except mysql.connector.Error as e:
        return jsonify({'success' : False , 'error' : f'Database error: {str(e)}'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        db.close()
    

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
       
        return redirect(url_for('home'))   
    username = session['username']

    device_info = "Unknown device"
    login_count_24h = 0
    active_users = []
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s",(username,))
            user_row = cursor.fetchone()
            
            if user_row: 
                user_id = user_row[0]
                
                cursor.execute( "SELECT device_info FROM login_logs WHERE user_id = %s ORDER BY login_time DESC LIMIT 1",
                    (user_id,))
                device_row = cursor.fetchone()
                if device_row:
                    device_info = device_row[0]
                cursor.execute(
                    "SELECT COUNT(*) FROM login_logs WHERE user_id = %s AND login_time > NOW() - INTERVAL 24 HOUR",
                    (user_id,)
                )
                login_count_24h = cursor.fetchone()[0]

            cursor.execute("SELECT username FROM users WHERE is_active = 1")
            active_users = [row[0] for row in cursor.fetchall()] 
        except mysql.connector.Error as e:
            print(f"Error fetching dashboard data: ",e)
        finally:
            if 'cursor' in locals():
                cursor.close()
            db.close()
    return render_template('dashboard.html',
                           username=username,
                           device_info=device_info,
                           login_count_24h=login_count_24h,
                           active_users=active_users)   
@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']
        db = get_db_connection()
        if db:
            try:
                cursor = db.cursor()
                cursor.execute("UPDATE users SET is_active = 0 WHERE username = %s",(username,))
                db.commit()
            except mysql.connector.Error as e:
                print(f"Error deactivating user:" , e)
            finally:
                if 'cursor' in locals():
                    cursor.close()
                db.close()
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)