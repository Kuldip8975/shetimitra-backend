# import mysql.connector

# def get_db_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="root",
#         database="shetimitra_ai",
#         port=3307
#     )

import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="maglev.proxy.rlwy.net",
        user="root",
        password="lDbWPNBuAVYIXZiBbXObZxsFNjjEQAJQ",
        database="railway",
        port=52515
    )
