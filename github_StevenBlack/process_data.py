# run "python .\process_data.py -u <url>" to run the tool

import requests
import sys


def process_data(raw_data: str) -> list:
    # remove all lines which are localhost, broadcast, and starting with #
    processed_data = [
        line for line in raw_data.splitlines() if
        "#" not in line and
        "::" not in line and
        "127.0.0.1 local" not in line and
        "255.255.255.255" not in line and
        "0.0.0.0 0.0.0.0" not in line
    ]
    # remove all empty strings
    while ("" in processed_data):
        processed_data.remove("")

    return processed_data


def main(url: str):
    # url = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
    response = requests.get(url).text
    processed_data = process_data(response)

    with open("processed_github.txt", mode="a", encoding="utf-16") as output:
        for line in processed_data:
            output.write(f"{line}\n")


if __name__ == "__main__":
    try:
        main(sys.argv[2])
    except IndexError:
        print("Please include an url!")
