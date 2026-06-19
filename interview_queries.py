import json
import mysql.connector
from database import get_db_connection
def save_interview(user_id, domain, difficulty, qa_pairs, evaluation, score, status):
    db = get_db_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        query = """
        INSERT INTO interviews (user_id, domain, difficulty, qa_data, evaluation, score, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id, 
            domain, 
            difficulty, 
            json.dumps(qa_pairs), 
            evaluation, 
            score, 
            status
        ))
        db.commit()
        return True
    except mysql.connector.Error as e:
        print("Database error in save_interview:", e)
        return False
    finally:
        cursor.close()
        db.close()

def get_interview_history(user_id):
    db = get_db_connection()
    if not db:
        return []
    try:
        # dictionary=True use karne se row dictionary form (key-value) mein aati hai
        cursor = db.cursor(dictionary=True)
        query = """
        SELECT id, domain, difficulty, score, status, timestamp, qa_data, evaluation
        FROM interviews
        WHERE user_id = %s
        ORDER BY timestamp DESC
        """
        cursor.execute(query, (user_id,))
        history = cursor.fetchall()
        return history
    except mysql.connector.Error as e:
        print("Database error in get_interview_history:", e)
        return []
    finally:
        cursor.close()
        db.close()


