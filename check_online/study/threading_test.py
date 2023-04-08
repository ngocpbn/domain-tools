from concurrent import futures


def do_sth(item: str):
    item = "aw " + item
    print(f"{item}")


with open("C:\\Users\\Admin\\Desktop\\get_bad_domain\\check_online\\inta.txt") as input:
    domains_ips = input.readlines()
    # print(domains_ips)
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        # nums = [i for i in range(0, 5)]
        executor.map(do_sth, domains_ips)
