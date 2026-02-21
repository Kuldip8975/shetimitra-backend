from db import get_db_connection

try:
    conn = get_db_connection()
    print("✅ DATABASE CONNECTED SUCCESSFULLY")
    conn.close()
except Exception as e:
    print("❌ ERROR:", e)