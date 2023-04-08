# This tool will check whether a domain or an IP is still working or not
# In Windows, type "python check_domains_ips.py -i "C:/path/to/input" to run

import socket
import sys
from concurrent import futures
import os


output = {
    "ipv4": "",
    "ipv6": "",
    "domains": "",
    "null_ipv4": "",
    "null_ipv6": "",
    "null_domains": "",
    "error": ""
}

current_dir = os.getcwd()
output_folder = "output"
output_dir = os.path.join(current_dir, output_folder)
if (not os.path.exists(output_dir)):
    os.mkdir(output_dir)


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
    global output
    item = item.replace("\n", "")
    # one function to check for special character in input
    category_id = categorize_input(item)
    if ((category_id == 4) and (not private_ip(item))):      # IPv4
        ports = [443, 80]
        for port in ports:
            telnet_result = telnet(item, port, 20)
            if (telnet_result == 1):
                if (item not in output["ipv4"]):
                    output["ipv4"] = output["ipv4"] + '\n' + item
                break
            if (telnet_result == -1):
                print(
                    f"An error happened while examining {item}. Please pay more attention to this IP address.")
                if (item not in output["error"]):
                    output["error"] = output["error"] + '\n' + item
            if (port == 80 and telnet_result == 0):
                print(f"{item} is NULL!")
                if (item not in output["null_ipv4"]):
                    output["null_ipv4"] = output["null_ipv4"] + '\n' + item

    elif (category_id == 1):       # Domain
        ip_list = nslookup(item)
        if (ip_list):
            if (item not in output["domains"]):
                output["domains"] = output["domains"] + '\n' + item
            for ip in ip_list:
                ip_type = categorize_input(ip)
                if ((ip_type == 4) and (not private_ip(ip))):
                    if (ip not in output["ipv4"]):
                        output["ipv4"] = output["ipv4"] + '\n' + ip

                elif (ip_type == 6):
                    if (ip not in output["ipv6"]):
                        output["ipv6"] = output["ipv6"] + '\n' + ip

        else:
            print(f"{item} is null!")
            if (item not in output["null_domains"]):
                output["null_domains"] = output["null_domains"] + '\n' + item


if __name__ == "__main__":
    command_len = len(sys.argv)
    if ("-i" in sys.argv and command_len == 3):
        try:
            with open(sys.argv[2], mode="r", encoding="utf-8") as input:
                domains_ips = input.readlines()
                with futures.ThreadPoolExecutor(max_workers=100) as executor:
                    executor.map(process_input, domains_ips)
            # remove the first newline character in each output file
            for key, value in output.items():
                newline_at_beginning = False
                for character in value:
                    if character == "\n":
                        newline_at_beginning = True
                        break

                if (newline_at_beginning):
                    output[key] = value[1:]

            for key, value in output.items():
                if (value != ''):
                    if ("\n\n" in value):
                        output[key] = output[key].replace("\n\n", "\n")
                    with open(f'{output_dir}\\{key}.txt', mode="w") as output:
                        output.write(value)

        except FileNotFoundError:
            print(f"{sys.argv[2]} doesn't exist!")
    else:
        print("Please specify an input file!")
