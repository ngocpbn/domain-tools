import requests
import json
from datetime import datetime
import psycopg2

connection = psycopg2.connect(database="ncsc",
                              host="127.0.0.1",
                              user="postgres",
                              password="postgres",
                              port="5432")
cur = connection.cursor()

cur.execute("select * from data")
data = cur.fetchall()
for row in data:
    with open(r"C:\\Users\Admin\Desktop\Work\\ncsc\data.txt", mode='a', encoding='utf-16') as file:
        file.write(f"{str(row)}\n")
