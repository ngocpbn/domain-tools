import requests
import json


def request_virustotal(domain: str) -> dict:
    # get a domain report from virustotal
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {
        "accept": "application/json",
        "x-apikey": "809d8dc201ffa69c6f1bc03d724f1ef40defc1870fe3d43f710c2cee1c075f0f"
    }

    response = requests.get(url, headers=headers)
    domain_analysis = json.loads(response.text)
    return domain_analysis

# domain_analysis will look like this:
# {
#     "data": {
#         "attributes": {
#             "last_dns_records": [bla bla bla],
#             "whois": "blablabla"
#             .....
#             "last_analysis_results": {
#                 "Kaspersky": {
#                     "category": "harmless"/"malicious"/"unrated",
#                     "result": "clean"/"unrated"/"malicious"/"malware",
#                     "method": "blacklist"/etc.,
#                     "engine_name": "Kaspersky"
#                 },
#                 bla bla bla
#             }
#             bla bla bla
#         }
#         bla bla bla
#     }
# }


def security_result(vendors_analysis: dict) -> int:
    famous_vendors = ["ESET", "G-Data", "Kaspersky",
                      "Fortinet", "Sophos", "Avira", "Bitdefender"]
    malicious_count = 0
    if (vendors_analysis is not None):
        for vendor in famous_vendors:
            vendor_security_analysis = vendors_analysis.get(vendor)
            if (vendor_security_analysis is not None):
                security_result = vendor_security_analysis.get("category")
                if (security_result == "malicious"):
                    malicious_count += 1
    else:
        print("Vendors' analysis is null!")
        malicious_count = -1

    return malicious_count

# test
# malicious to a lot of vendors
# tube8vidszyj.ddns.name --> 3 largest vendors ESET, G-Data, and Kaspersky tells that it's harmless, while other mid-level vendors say it's malicious
# Dr.Web says it's malicious too

# harmless:
# tdcv3.talkingdata.net


def main() -> None:
    domain = "tube8vidszyj.ddns.name"       # thong nhat input vs chi Trang sau
    result = request_virustotal(domain)

    vendors_analysis = result.get("data").get(
        "attributes").get("last_analysis_results")

    malicious_count = security_result(vendors_analysis)

    if (malicious_count == -1):
        print("Error! Vendor's analysis is null.")
    elif (malicious_count <= 1):
        with open("whitelist.txt", mode="a", encoding="utf-16") as whitelist:
            whitelist.write(f"{domain}\n")
    elif (malicious_count == 2):
        with open("graylist.txt", mode="a", encoding="utf-16") as graylist:
            graylist.write(f"{domain}\n")
    else:
        with open("blacklist.txt", mode="a", encoding="utf-16") as blacklist:
            blacklist.write(f"{domain}\n")


if __name__ == "__main__":
    main()
