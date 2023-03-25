import requests
import json
from datetime import datetime
import psycopg2
# import threading
import sys


connection = psycopg2.connect(database="ncsc",
                              host="127.0.0.1",
                              user="postgres",
                              password="postgres",
                              port="5432")
cur = connection.cursor()

conf = {
    'user_name': 'scs_openapi',
    'password': 'yqTd7HbBhkryzMAP',
    'api_key': 'mboz8Q3FioCoE6RjoD8t',
    'delta': 0,
    'url': 'https://openapi.ncsc.gov.vn/phishing/query'
}


def request_ncsc(page: int, delta=conf['delta']) -> dict | None:
    response = requests.get(url=f'{conf["url"]}?api_key={conf["api_key"]}&page={page}&delta_day={delta}',
                            auth=(conf["user_name"], conf["password"]))
    if response.status_code == 200:
        response_text = json.loads(response.text)
        if (response_text == f"Cannot found page {page}"):
            print(f"Page {page} of day {delta} doesn't have data.")
            return None
        else:
            return response_text
    else:
        return None


def process_data_and_upsert(records: list[dict]):
    for record in records:
        url = record.get('url')
        if url == None:
            url = record.get('domain')

        url = url.replace('www.', '').replace(
            'http://', '').replace('https://', '')
        substrings = url.split('/')
        if '' in substrings:
            substrings.remove('')

        if (len(substrings) > 1):
            continue
        else:
            url = url.replace('/', '')
            timestamp = str(datetime.now()).split(".")[0]
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
                        (timestamp, url, record.get('ip'), record.get('tags'), record.get('confident_level'), record.get('verified'), record.get(
                            'online'), record.get('data_source'), record.get('created_at'), record.get('last_updated'))
                        )

            connection.commit()

            today = timestamp.split(" ")[0]
            cur.execute(
                "select timestamps, url, tags from data where timestamps like %s", (today,))
            urls_and_tags = cur.fetchall()
            print(urls_and_tags)
            for row in urls_and_tags:
                domain = row[1]
                tags = row[2].replace("{", "").replace("}", "").replace(
                    "[", '').replace(']', '').replace("'", "").replace(" ", "_").replace('"', '')
                tags = tags.split(",")
                # The first tag in the list of tags will be chosen as the name of the record file
                file_name = tags[0]

                with open(f"C:\\Users\\Admin\\Desktop\\Work\\record\\{file_name}.txt", mode='a', encoding='utf-16') as record_file:
                    print(f"Appending to {file_name}.txt")
                    record_file.write(
                        f"{domain}      IN             CNAME       canhbao.safegate.vn.\n")
                    record_file.write(
                        f"www.{domain}      IN             CNAME       canhbao.safegate.vn.\n")


def main(start: int, end: int, initial_page: "int" = 1):
    for day in range(int(start), int(end) + 1):
        first_request = request_ncsc(initial_page, day)
        # first_request will look like this
        # first_request = {
        #     'records': [
        #         {'url': 'https://vaytienhoatoc247.com/', 'ip': '104.21.28.213', 'tags': ['scam'], 'confident_level': 'high', 'verified': True, 'online': True, 'data_source': 'Chong lua dao', 'created_at': '09-02-2023 01:16:48', 'last_updated': '09-02-2023 01:16:48'},
        #           ...
        #             ],
        #     'record_count': 180,
        #     'meta': {
        #         'total_pages': 2,
        #         'page': 1
        #         }
        # }

        if (first_request is not None):
            process_data_and_upsert(first_request.get(
                'records'))          # process data here
            timestamp = str(datetime.now()).split(".")[0]
            print(f"{timestamp}: done with day {day}, page {initial_page}")
            total_pages = first_request.get('meta').get('total_pages')

            for page in range(int(initial_page) + 1, total_pages+1):
                another_request = request_ncsc(page, day)
                process_data_and_upsert(another_request.get('records'))
                timestamp = str(datetime.now()).split(".")[0]
                print(f"{timestamp}: done with day {day}, page {page}.")


if __name__ == "__main__":
    args = []

    for i in range(1, len(sys.argv)):
        flag = sys.argv[i]
        if flag == '-s' or flag == '--start':
            args.append(sys.argv[i+1])

        if flag == '-e' or flag == '--end':
            args.append(sys.argv[i+1])

        if flag == '-p' or flag == '--page':
            args.append(sys.argv[i+1])

    if len(args) == 3:
        main(start=args[0], end=args[1], initial_page=args[2])
    else:
        main(start=args[0], end=args[1])
