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
        
        insert_query = "INSERT INTO users(username, email, password) VALUES (%s, %s, %s)"
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