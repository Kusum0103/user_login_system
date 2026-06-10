import sys
import mysql.connector
from database import get_db_connection
from auth import is_valid_email, check_password_strength, check_username_exists, register_user 

def main() :
    mydb = get_db_connection()
    if not mydb:
        print("Error: Could not connect to database. Please check your connection and try again")
        sys.exit() 
    cursor = mydb.cursor(buffered=True)

    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    confirm_password = input("Confirm password: ")
    if not is_valid_email(email):
        print("Error: Invalid email format.")
        sys.exit()

    is_strong, password_strength_message = check_password_strength(password)
    if not is_strong:
        print("Error:Password does not meet complexity requirement.")
        print(password_strength_message)
        sys.exit()
  
    if password != confirm_password:
        print("Error: Passwords do not match.")
        sys.exit()
    
    if check_username_exists(cursor, username):
        print("Error: Username already exists.")
        sys.exit()
    try:
        register_user(mydb,cursor,username,email,password)
        print("Registration successful!")
    except mysql.connector.Error as e:
        print("An Error occured during SignUp:", e)
    finally: 
           cursor.close()
           mydb.close()
if __name__ == "__main__":
    main()  