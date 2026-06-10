import re
import bcrypt

def is_valid_email(email):
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern,email)) 

def check_password_strength(password):
    if len(password) < 8:
        return False,"Password must be at least 8 characters long."
    if not any(char.isupper() for char in password):
        return False,"Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit."
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>/?~" 
    if not any(char in special_chars for char in password):
        return False, "Password must contain at least one special character." 
    return True, "Strong Password."
def check_username_exists(cursor, username):
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone() 
    return result is not None

def register_user(mydb, cursor, username, email, password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes,salt)
    hashed_password_str = hashed_password.decode('utf-8')
    insert_query = "INSERT INTO users(username, email, password) VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (username, email, hashed_password_str)) 
    mydb.commit()  

def verify_user_login(cursor, username, password):
    query = "SELECT password FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if not result:
        return False , "Invalid username or password."
    stored_hash_str = result[0]
    stored_hash_bytes = stored_hash_str.encode('utf-8')
    password_bytes = password.encode('utf-8')
    if bcrypt.checkpw(password_bytes, stored_hash_bytes):
        return True, "Login Successful.🎉"
    else:
        return False, "Invalid username or password."