import mysql.connector
from config import DB_CONFIG
import json

def get_db_connection():
    try:
        mydb = mysql.connector.connect(**DB_CONFIG)
        return mydb
    except mysql.connector.Error as e:
        print("Database Connection Error:", e)
        return None

def init_db():
    db = get_db_connection()
    if not db:
        print("Failed to connect to MySQL to initialize schema.")
        return
    
    try:
        cursor = db.cursor()

        #users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            is_active TINYINT(1) DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        #login logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            device_info VARCHAR(255),
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # interviews table 
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            domain VARCHAR(255),
            difficulty VARCHAR(100),
            qa_data LONGTEXT,
            evaluation LONGTEXT,
            score INT NULL,
            status VARCHAR(100),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        db.commit()
        print("MySQL 'interviews' table initialized successfully.")
        
    except mysql.connector.Error as err:
        print(f"MySQL error during database initialization: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        db.close()


