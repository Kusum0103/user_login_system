import re
import bcrypt
import secrets

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


def generate_reset_token():
    
    return secrets.token_urlsafe(32)

def hash_password(password):
  
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')
