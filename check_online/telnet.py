import socket


host = "31.13.4.174"

# try:
#     print("1")
#     socket.create_connection((host, 443), timeout=10)
#     with open("valid_ips_domains.txt", mode="a", encoding="utf-16") as valid_output:
#         valid_output.write(f"{host}\n")
# except socket.timeout:
#     try:
#         print("2")
#         socket.create_connection((host, 443), timeout=100)
#         with open("valid_ips_domains.txt", mode="a", encoding="utf-16") as valid_output:
#             valid_output.write(f"{host}\n")
#     except socket.timeout:
#         try:
#             print("3")
#             socket.create_connection((host, 80), timeout=10)
#             with open("valid_ips_domains.txt", mode="a", encoding="utf-16") as valid_output:
#                 valid_output.write(f"{host}\n")
#         except socket.timeout:
#             try:
#                 print("4")
#                 socket.create_connection((host, 80), timeout=100)
#                 with open("valid_ips_domains.txt", mode="a", encoding="utf-16") as valid_output:
#                     valid_output.write(f"{host}\n")
#             except socket.timeout:


#                 with open("invalid_ips_domains.txt", mode="a", encoding="utf-16") as invalid_output:
#                     invalid_output.write(f"{host}\n")
# except:
#     print("Unknown error.")


ports = [443, 80]


def telnet(host: str, port: int, timeout: int) -> int:
    try:
        socket.create_connection((host, port), timeout)
        return 1
    except socket.timeout:
        if (timeout == 100):
            return 0
        else:
            outer_result = telnet(host, port, timeout*10)
            if (outer_result == 1):
                return 1
            elif (outer_result == 0):
                return 0
            else:
                return -1

    except:
        # all kinds of other errors. For example: "[WinError 10061] No connection could be made because the target machine actively refused it."
        return -1


ports = [443, 80]
for port in ports:
    telnet_result = telnet(host, port, 10)
    if (telnet_result == 1):
        with open("valid_ips_domains.txt", mode="a", encoding="utf-16") as valid_output:
            valid_output.write(f"{host}\n")
        break
    if (telnet_result == -1):
        print(
            f"An error happened while examining {host}. Please pay more attention to this IP address.")
        with open("need_more_attention.txt", mode="a", encoding="utf-16") as attention:
            attention.write(f"{host}\n")
    if (port == 80 and telnet_result == 0):
        print(f"{host} is NULL!")
        with open("invalid_ips_domains.txt", mode="a", encoding="utf-16") as invalid_output:
            invalid_output.write(f"{host}\n")
