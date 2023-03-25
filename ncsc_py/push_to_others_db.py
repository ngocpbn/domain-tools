import psycopg2

connection = psycopg2.connect(database="ncsc",
                              host="127.0.0.1",
                              user="postgres",
                              password="postgres",
                              port="5432")
cur = connection.cursor()


with open(f"C:\\Users\\Admin\\Desktop\\Work\\ncsc\\data.txt", mode='r', encoding='utf-16') as file:
    for line in file:
        data = eval(line)
        # print(data[0])
        cur.execute("""INSERT INTO data (
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
                ON CONFLICT (url) DO NOTHING""",
                    (data[0], data[1], data[2], data[3], data[4],
                     data[5], data[6], data[7], data[8], data[9])
                    )
    connection.commit()

connection.close()
