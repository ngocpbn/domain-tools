import psycopg2
from datetime import datetime

#Establishing the connection
conn = psycopg2.connect(
   database="ncsc", user='postgres', password='postgres', host='192.168.25.132', port= '5432'
)
#Creating a cursor object using the cursor() method
cur = conn.cursor()

sql = '''select url, ip, tags, confident_level, verified, online, data_source, created_at, last_updated from data'''

cur.execute(sql)
result = cur.fetchall()
conn.close()

local_db = psycopg2.connect(
   database="ncsc", user='postgres', password='postgres', host='127.0.0.1', port= '5432'
)

cursor = local_db.cursor()

count = 0
for row in result:
    url = row[0]
    ip = row[1]
    
    tags = row[2].replace('{', '').replace('}', '').replace('"','')
    tags = tags.split(',')
    tags = str(tags)
    
    confident_level = row[3]
    verified = row[4]
    online = row[5]
    data_source = row[6]
    created_at = row[7]
    last_updated = row[8]
    timestamp = datetime.now()
    
    cursor.execute("""INSERT INTO data (
                timestamps, 
                url, 
                ip, 
                tags, 
                confident_level, 
                verified, 
                online, 
                data_source, 
                created_at, 
                last_updated
                ) 
                VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s) 
                ON CONFLICT (url) DO UPDATE SET timestamps=%s""", 
                (timestamp, url, ip,tags, confident_level, verified, online,data_source,created_at,last_updated,timestamp)
            )
    local_db.commit()
    try:
        print(row)
    except:
        print("Unicode problem")
        
    count += 1

print(count)

local_db.close()