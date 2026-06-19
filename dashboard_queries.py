import mysql.connector
from database import get_db_connection


def get_dashboard_stats(user_id):
    db = get_db_connection()
    stats = {
        'device_info' : "Unknown device",
        'login_count_24h' : 0,
    }
    if not db:
        return stats
    try:
        cursor = db.cursor()

        cursor.execute(
            "SELECT device_info FROM login_logs WHERE user_id = %s ORDER BY login_time DESC LIMIT 1",
            (user_id,)
        )
        device_row = cursor.fetchone()
        if device_row:
            stats['device_info'] = device_row[0]

        cursor.execute(
            "SELECT COUNT(*) FROM login_logs WHERE user_id = %s AND login_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)",
            (user_id,)
        )
        count_row = cursor.fetchone()
        if count_row: 
            stats['login_count_24h'] = count_row[0]
        return stats

    except mysql.connector.Error as e:
        print("Database error in get_dashboard_stats:", e)
        return stats
    finally:
        cursor.close()
        db.close()
        
    
def get_active_users():
    db = get_db_connection()
    if not db :
        return[]
    try:
        cursor = db.cursor()
        query = "SELECT username FROM users WHERE is_active = 1"
        cursor.execute(query)
        active_users = [row[0] for row in cursor.fetchall()]
        return active_users
        
    except mysql.connector.Error as e:
        print("Database error in get_active_users:", e)
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        db.close()

