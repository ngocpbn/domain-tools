import requests
import json
from datetime import datetime
import psycopg2
import sys
import os
from pathlib import Path


current_dir = os.getcwd()
output_folder = "output"
output_dir = os.path.join(current_dir, output_folder)
if (not os.path.exists(output_dir)):
    os.mkdir(output_dir)

output_container = {

}

connection = psycopg2.connect(database="ncsc",
                              host="127.0.0.1",
                              user="postgres",
                              password="postgres",
                              port="5432")
cur = connection.cursor()

conf = {
    'user_name': 'scs_openapi',
    'password': 'yqTd7HbBhkryzMAP',
    'api_key': 'bee4a797-e868-4f1c-b7d9-60dc8b87cbef',
    'delta': 0,
    'url': "https://openapi.ncsc.gov.vn/phishing/query"
}


def request_ncsc(delta=conf['delta']) -> dict | None:
    response = requests.get(
        url=f'{conf["url"]}?api_key={conf["api_key"]}&delta_day={delta}',
        auth=(
            conf["user_name"],
            conf["password"]
        )
    )
    # API url will look like this: https://openapi.ncsc.gov.vn/phishing/query?api_key=bee4a797-e868-4f1c-b7d9-60dc8b87cbef&delta_day=1

    if response.status_code == 200:
        response_text = json.loads(response.text)
        if (response_text == []):
            print(f"Day {delta} doesn't have data.")
            return None
        else:
            return response_text
    else:
        print(f"Status code {response.status_code}")
        return None
    # OLD API URL: https://openapi.ncsc.gov.vn/phishing/query?api_key=mboz8Q3FioCoE6RjoD8t&page=1&delta_day=10


def process_data_and_upsert(records: list[dict]) -> None:
    for record in records:
        domain = record.get('domain')
        timestamp = str(datetime.now()).split(".")[0]
        cur.execute("""INSERT INTO data (
                        timestamps, 
                        domain, 
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
                        ON CONFLICT (domain) DO NOTHING""",
                    (timestamp, domain, record.get('ip'), record.get('tags'), record.get('confident_level'), record.get(
                        'verified'), record.get('online'), record.get('data_source'), record.get('created_at'), record.get('last_updated'))
                    )

        connection.commit()

        # Update the record file
        today = timestamp.split(" ")[0]
        query = "select timestamps, domain, tags from data where timestamps like '" + today + "%'"
        cur.execute(query)
        domains_and_tags = cur.fetchall()
        for row in domains_and_tags:
            domain = row[1]
            tags = row[2].replace("{", "").replace("}", "").replace(
                "[", '').replace(']', '').replace("'", "").replace(" ", "_").replace('"', '')
            tags = tags.split(",")
            # The first tag in the list of tags will be chosen as the name of the record file
            file_name = tags[0]

            domain = domain.replace("www.", "")
            records = [domain,
                       "www." + domain]
            if (output_container.get(file_name) is None):
                output_container[file_name] = []

            for record in records:
                if (record not in output_container[file_name]):
                    output_container[file_name].append(record)


def main(start: int, end: int) -> None:
    for day in range(int(start), int(end) + 1):
        api_request = request_ncsc(day)
        # api_request = [
        #     {
        #         "url": "https://sinhvientainangnam2021.weebly.com",
        #         "domain": "sinhvientainangnam2021.weebly.com",
        #         "online": false,
        #         "ip": null,
        #         "tags": [
        #             "phishing"
        #         ],
        #         "target_brand": "Facebook",
        #         "verified": true,
        #         "confident": "high",
        #         "source": "Tin Nhiem Mang",
        #         "created": "2021-08-22 00:00:00",
        #         "updated": "2023-04-27 09:17:08"
        #     },
        #     .......
        # ]

        if (api_request is not None):
            timestamp = str(datetime.now()).split(".")[0]
            print(f"{timestamp}: Day {day}")
            process_data_and_upsert(api_request)


if __name__ == "__main__":
    args = []

    for i in range(1, len(sys.argv)):
        flag = sys.argv[i]
        if flag == '-s' or flag == '--start':
            args.append(sys.argv[i+1])

        if flag == '-e' or flag == '--end':
            args.append(sys.argv[i+1])

    if len(args) == 2:
        entries = Path(output_dir)
        for entry in entries.iterdir():
            if (entry.is_file()):
                with open(entry, mode="r") as file:
                    content = file.readlines()
                    output_container[entry.name.replace(".txt", "")] = []
                    try:
                        index = content.index(
                            '@       IN              NS              localhost.\n')
                        if (content[index+1] == "\n"):
                            index += 2
                    except:
                        index = 0

                    for domain in content[index:]:
                        domain = domain.replace(
                            "      IN             CNAME       canhbao.safegate.vn.\n", "")
                        output_container[entry.name.replace(
                            ".txt", "")].append(domain)

        main(start=args[0], end=args[1])

        for key, value in output_container.items():
            output_file = f'{output_dir}\\{key}.txt'

            with open(output_file, mode="w") as output:
                output.write("$TTL 1D\n@       IN      SOA     spoof.safegate.vn. safegate.vn. (\n                        2023011101      ; serial\n                        3H              ; refresh\n                        1H              ; retry\n                        3D              ; expire\n                        1H              ; minimum\n                        )\n@       IN              NS              localhost.\n\n")
                for item in value:
                    try:
                        output.write(
                            item + "      IN             CNAME       canhbao.safegate.vn.\n")
                    except:
                        print("Unicode error while writing domain " +
                              item + " to file " + output_file + ".")

    else:
        print("Please include both starting and ending day!")
