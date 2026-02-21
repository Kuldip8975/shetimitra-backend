from db import get_db_connection

# SQL file path
sql_file = "shetimitra_ai.sql"

conn = get_db_connection()
cursor = conn.cursor()

with open(sql_file, "r", encoding="utf-8") as f:
    sql_script = f.read()

# statements split करून execute
for statement in sql_script.split(";"):
    stmt = statement.strip()
    if stmt:
        try:
            cursor.execute(stmt)
        except Exception as e:
            print("Error:", e)

conn.commit()
cursor.close()
conn.close()

print("✅ DATABASE IMPORTED SUCCESSFULLY")