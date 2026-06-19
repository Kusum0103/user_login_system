import re

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
