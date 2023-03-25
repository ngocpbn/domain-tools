import psycopg2

#Establishing the connection
conn = psycopg2.connect(
   database="ncsc", user='postgres', password='postgres', host='127.0.0.1', port= '5432'
)
#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Creating table as per requirement
sql ='''CREATE TABLE data(
    timestamps varchar(40),
    url varchar(200) PRIMARY KEY, 
    ip varchar(40), 
    tags varchar(100), 
    confident_level varchar(40), 
    verified varchar(40), 
    online varchar(40), 
    data_source varchar(40), 
    created_at varchar(40), 
    last_updated varchar(40)
)'''
cursor.execute(sql)
print("Table created successfully........")
conn.commit()
#Closing the connection
conn.close()