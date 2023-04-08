ip_list = ["192.168.0.1", "192.168.15.1",
           "17.12.43.6", "172.16.25.2", "172.20.44.1", "10.1.3.5", "12.4.65.3", "12.10.54.6", "151.101.129.84"]


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


for ip in ip_list:
    if (not private_ip(ip)):
        print(f"{ip} is public")
