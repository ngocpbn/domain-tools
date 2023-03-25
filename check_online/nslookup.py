import socket

domain = "facebook.com"

ip_list = []
try:
    ais = socket.getaddrinfo(domain, 0, 0, 0, 0)
    for result in ais:
        ip_list.append(result[-1][0])
    ip_list = list(set(ip_list))
    print(ip_list)
    # with open("valid_ips_domains.txt", mode="a", encoding="utf-16") as valid_output:
    #     valid_output.write(f"{domain}\n")
except socket.gaierror:
    print(f"{domain} is null!")
    # with open("invalid_ips_domains.txt", mode="a", encoding="utf-16") as invalid_ouput:
    #     invalid_ouput.write(f"{domain}\n")

############################################################
# sample:
# ais = socket.getaddrinfo(
#     host=domain,
#     port=port,
#     family=socket.AF_INET,
#     type=0,
#     proto=socket.IPPROTO_TCP,
#     flags=socket.AI_CANONNAME
# )
