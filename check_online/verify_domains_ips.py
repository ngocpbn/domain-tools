# This tool will check whether a domain or an IP is still working or not
# In Windows, type "python verify_domains_ips.py -i "C:/path/to/input" to run

import socket
import sys
from concurrent import futures
import os


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
        if (timeout == 200):
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
    with open(file_name, mode="a", encoding="utf-8") as file:
        # use utf-8 or utf-16le or utf-16be to prevent Python from adding "\ufeff" to the beginning of a string while writing to file. (encode without BOM)
        # refer to this for more info: https://stackoverflow.com/questions/17912307/u-ufeff-in-python-string
        file.write(f"\n{item}")
        # Place newline character at the beginning of the string to avoid trailing newlines


def private_ip(ip: str) -> bool:
    octets = ip.split(".")
    first_octet = int(octets[0])
    second_octet = int(octets[1])
    if ((192 == first_octet) and (168 == second_octet)):
        return True
    elif (10 == first_octet):
        return True
    elif ((172 == first_octet) and (16 <= second_octet) and (second_octet <= 31)):
        return True

    return False


def process_input(item: str) -> None:
    item = item.replace("\n", "")
    category_id = categorize_input(item)
    if ((category_id == 4) and (not private_ip(item))):      # IPv4
        ports = [443, 80]
        for port in ports:
            telnet_result = telnet(item, port, 20)
            if (telnet_result == 1):
                append_to_file("valid_ipv4.txt", item)
                break
            if (telnet_result == -1):
                print(
                    f"An error happened while examining {item}. Please pay more attention to this IP address.")
                append_to_file("need_more_attention.txt", item)
            if (port == 80 and telnet_result == 0):
                print(f"{item} is NULL!")
                append_to_file("invalid_ipv4.txt", item)

    elif (category_id == 1):       # Domain
        ip_list = nslookup(item)
        if (ip_list):
            append_to_file("valid_domains.txt", item)
            for ip in ip_list:
                ip_type = categorize_input(ip)
                if ((ip_type == 4) and (not private_ip(item))):
                    append_to_file("valid_ipv4.txt", ip)
                elif (ip_type == 6):
                    append_to_file("valid_ipv6.txt", ip)
        else:
            print(f"{item} is null!")
            append_to_file("invalid_domains.txt", item)


if __name__ == "__main__":
    command_len = len(sys.argv)
    if ("-i" in sys.argv and command_len == 3):
        try:
            file_names = ["valid_ipv4.txt", "invalid_ipv4.txt", "valid_domains.txt",
                          "invalid_domains.txt", "valid_ipv6.txt", "invalid_ipv6.txt", "need_more_attention.txt"]
            for file_name in file_names:
                if (os.path.exists(file_name)):
                    os.remove(file_name)
            with open(sys.argv[2], mode="r", encoding="utf-8") as input:
                domains_ips = input.readlines()
                with futures.ThreadPoolExecutor(max_workers=100) as executor:
                    executor.map(process_input, domains_ips)
            # remove the first newline in each output file
            # for file_name in file_names:
            #     if (os.path.exists(file_name)):

        except FileNotFoundError:
            print(f"{sys.argv[2]} doesn't exist!")
    else:
        print("Please specify an input file!")
