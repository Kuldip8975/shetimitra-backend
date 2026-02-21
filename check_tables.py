from db import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SHOW TABLES")
for t in cursor.fetchall():
    print(t)

conn.close()