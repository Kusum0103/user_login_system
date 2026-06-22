import mysql.connector
import bcrypt
from database import get_db_connection

def get_user_id_by_username(username):
    db = get_db_connection()
    if not db:
        return None
    try:
        cursor = db.cursor()
        query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        return row[0] if row else None
    except mysql.connector.Error as e:
        print("Database error in get_user_id_by_username:", e)
        return None
    finally:
        cursor.close()
        db.close()

def update_user_active_status(is_active, user_id=None, username=None):
    if user_id is None and username is None:
        return False
        
    db = get_db_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        if user_id is not None:
            query = "UPDATE users SET is_active = %s WHERE id = %s"
            cursor.execute(query, (is_active, user_id))
        elif username is not None:
            query = "UPDATE users SET is_active = %s WHERE username = %s"
            cursor.execute(query, (is_active, username))
        db.commit()
        return True
    except mysql.connector.Error as e:
        print("Database error in update_user_active_status:", e)
        return False
    finally:
        cursor.close()
        db.close()


def log_login_activity(user_id, device_info):
    db = get_db_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        query = "INSERT INTO login_logs (user_id, device_info) VALUES (%s, %s)"
        cursor.execute(query, (user_id, device_info))
        db.commit()
        return True
    except mysql.connector.Error as e:
        print("Database error in log_login_activity:", e)
        return False
    finally:
        cursor.close()
        db.close()


def check_username_exists(username):
    db = get_db_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        return result is not None
    except mysql.connector.Error as e:
        print("Database error in check_username_exists:", e)
        return False
    finally:
        cursor.close()
        db.close()


def register_user(username, email, password):
    db = get_db_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        hashed_password_str = hashed_password.decode('utf-8')
        
        insert_query = "INSERT INTO users(username, email, password, is_verified) VALUES (%s, %s, %s, 1)"
        cursor.execute(insert_query, (username, email, hashed_password_str)) 
        db.commit()  
        return True
    except mysql.connector.Error as e:
        print("Database error in register_user:", e)
        return False
    finally:
        cursor.close()
        db.close()

def verify_user_login(username, password):

    db = get_db_connection()
    if not db:
        return False, "Database connection failed"
    try:
        cursor = db.cursor()
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        if not result:
            return False,"Invalid username or password."
        stored_hash_str = result[0]
        stored_hash_bytes = stored_hash_str.encode('utf-8')
        password_bytes = password.encode('utf-8')
        if bcrypt.checkpw(password_bytes, stored_hash_bytes):
            return True, "Login successfull 🎉"
        else:
            return False, "Invalid username or password."
    except mysql.connector.Error as e:
        print("Database error in verify_user_login:", e)
        return False , f"Database error: {str(e)}"
    finally:
        cursor.close()
        db.close()

from datetime import datetime
def save_otp(username, otp , expiry_time):
    db = get_db_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        query = "UPDATE users SET otp_code = %s, otp_expiry = %s WHERE username = %s"
        cursor.execute(query, (otp, expiry_time, username))  
        db.commit()
        return True
    except mysql.connector.Error as e:
        print("Database error in save_otp:", e)
        return False
    finally:
        cursor.close()
        db.close()

def verify_otp_in_db(username , otp):
    db = get_db_connection()
    if not db :
        return False , "Database connection failed"
    try:
        cursor = db.cursor()
        query = "SELECT otp_code , otp_expiry FROM users WHERE username = %s"
        cursor.execute(query , (username,))
        result = cursor.fetchone()
        if not result or not result [0]:
            return False , "Invalid OTP. No OTP record found for this user."
        
        db_otp , db_expiry = result[0], result [1]
        
        if db_otp != otp :
            return False , "Invalid OTP. Does not match."
        
        if datetime.now()> db_expiry:
            return False, "OTP expired. Please request a new one."
        
       

        update_query = """ UPDATE users SET is_verified = 1, otp_code = NULL, otp_expiry = NULL WHERE username = %s"""
        cursor.execute(update_query , (username,))  
        db.commit()
        return True, "OTP verified successfully"

    except mysql.connector.Error as e:
        print("Database error in verify_otp_in_db:", e)
        return False , f"Database error: {str(e)}"
    finally:
        cursor.close()
        db.close()

def is_user_verified(username):
    db = get_db_connection()
    if not db :
        return False

    try:
        cursor = db.cursor()
        query = "SELECT is_verified FROM users WHERE username = %s"
        cursor.execute(query , (username,))
        result = cursor.fetchone()

        return result[0] if result else False

    except mysql.connector.Error as e:
        print("Database error in is_user_verified:", e)
        return False
    finally:
        cursor.close()
        db.close()

def get_user_email(username):
    db = get_db_connection()
    if not db:
        return None
    try:
        cursor = db.cursor()
        query = "SELECT email FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as e:
        print("Database error in get_user_email:", e)
        return None
    finally:
        cursor.close()
        db.close()
        


def delete_user_account(username):
    db = get_db_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        query = "DELETE FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        db.commit()
        return True
    except mysql.connector.Error as e:
        print("Database error in delete_user_account:", e)
        return False
    finally:
        cursor.close()
        db.close()
        
