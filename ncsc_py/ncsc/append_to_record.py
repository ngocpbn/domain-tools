import psycopg2


connection = psycopg2.connect(database="ncsc",
                              host="127.0.0.1",
                              user="postgres",
                              password="postgres",
                              port="5432")
cur = connection.cursor()

cur.execute(
    "select timestamps, url, tags from data where timestamps like '2023-3-13%'")
urls_and_tags = cur.fetchall()
print(urls_and_tags)
for row in urls_and_tags:
    domain = row[1]
    tags = row[2].replace("{", "").replace("}", "").replace(
        "[", '').replace(']', '').replace("'", "").replace(" ", "_").replace('"', '')
    tags = tags.split(",")
    file_name = tags[0]
    print(file_name)
    with open(f"C:\\Users\\Admin\\Desktop\\Work\\record\\march_13\\{file_name}.txt", mode='a', encoding='utf-16') as record_file:
        record_file.write(
            f"{domain}      IN             CNAME       canhbao.safegate.vn.\n")
        record_file.write(
            f"www.{domain}      IN             CNAME       canhbao.safegate.vn.\n")
