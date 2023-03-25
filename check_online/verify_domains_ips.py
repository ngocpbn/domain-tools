# This tool will check whether a domain or an IP is still working or not
# In Windows, type "python online_offline.py -i "C:/path/to/input" to run

import socket
import sys
from concurrent import futures


def categorize_input(item: str) -> int:
    if (":" in item):
        return 6        # 6 == ipv6
    substrings = item.split(".")
    if (len(substrings) == 4):
        contains_alphabet_letter = False
        for substring in substrings:
            for character in substring:
                if (character.isalpha()):
                    contains_alphabet_letter = True
                    break
            if contains_alphabet_letter:
                break

        if (not contains_alphabet_letter):
            return 4        # 4 == ipv4

    return 1        # 1 == domain


def nslookup(item: str) -> None:
    try:
        result = socket.getaddrinfo(item, 0, 0, 0, 0)
        ip_list = []
        for item in result:
            ip_list.append(item[-1][0])
        return ip_list
    except socket.gaierror:
        return 0


def telnet(host: str, port: int, timeout: int) -> int:
    try:
        socket.create_connection((host, port), timeout)
        return 1
    except socket.timeout:
        if (timeout == 100):
            return 0
        else:
            outer_result = telnet(host, port, timeout*10)
            # without these below returns, the outer function call will return None
            if (outer_result == 1):
                return 1
            elif (outer_result == 0):
                return 0
            else:
                return -1

    except:
        # all kinds of other errors. For example: "[WinError 10061] No connection could be made because the target machine actively refused it."
        return -1


def append_to_file(file_name: str, item: str) -> None:
    with open(file_name, mode="a", encoding="utf-16") as file:
        file.write(f"{item}\n")


def process_input(item: str) -> None:
    item = item.replace("\n", "")
    category_id = categorize_input(item)
    if (category_id == 4):      # IPv4
        ports = [443, 80]
        for port in ports:
            telnet_result = telnet(item, port, 10)
            if (telnet_result == 1):
                append_to_file("valid_ips_domains.txt", item)
                break
            if (telnet_result == -1):
                print(
                    f"An error happened while examining {item}. Please pay more attention to this IP address.")
                append_to_file("need_more_attention.txt", item)
            if (port == 80 and telnet_result == 0):
                print(f"{item} is NULL!")
                append_to_file("invalid_ips_domains.txt", item)

    elif (category_id == 1):       # Domain
        ip_list = nslookup(item)
        if (ip_list):
            append_to_file("valid_ips_domains.txt", item)
            for ip in ip_list:
                append_to_file("valid_ips_domains.txt", ip)
        else:
            print(f"{item} is null!")
            append_to_file("invalid_ips_domains.txt", item)


if __name__ == "__main__":
    command_len = len(sys.argv)
    if ("-i" in sys.argv and command_len == 3):
        try:
            with open(sys.argv[2], mode="r", encoding="utf-8") as input:
                domains_ips = input.readlines()
                with futures.ThreadPoolExecutor(max_workers=30) as executor:
                    executor.map(process_input, domains_ips)

        except FileNotFoundError:
            print(f"{sys.argv[2]} doesn't exist!")
    else:
        print("Please specify an input file!")
