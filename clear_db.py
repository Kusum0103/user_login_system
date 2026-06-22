import mysql.connector
from config import DB_CONFIG

try:
    # 1. Database se connect hona
    mydb = mysql.connector.connect(**DB_CONFIG)
    cursor = mydb.cursor()

    print("Connecting to database...")

    # 2. Foreign key checks ko band karna (taki tables delete hone se rokein na)
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    # 3. Saare data ko clear karna (Truncate se IDs bhi wapas 1 se shuru hongi)
    cursor.execute("TRUNCATE TABLE interviews;")
    cursor.execute("TRUNCATE TABLE login_logs;")
    cursor.execute("TRUNCATE TABLE users;")

    # 4. Checks ko wapas chalu karna
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    mydb.commit()
    print("🎉 Success: Database se saara purana data delete ho gaya hai!")

except mysql.connector.Error as e:
    print("Database error occurred:", e)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'mydb' in locals():
        mydb.close()
