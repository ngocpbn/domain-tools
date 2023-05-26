import sys
import os


output_container = []

current_dir = os.getcwd()
output_folder = "refined_output"
output_dir = os.path.join(current_dir, output_folder)
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

def contains_vnmese_char(a_str: str):
    vnmese_chars = [
        "Á",
        "À",
        "Ã",
        "Ạ",
        "Â",
        "Ấ",
        "Ầ",
        "Ẫ",
        "Ậ",
        "Ă",
        "Ắ",
        "Ằ",
        "Ẵ",
        "Ặ",
        "à",
        "á",
        "ạ",
        "ả",
        "ã",
        "â",
        "ầ",
        "ấ",
        "ậ",
        "ẩ",
        "ẫ",
        "ă",
        "ằ",
        "ắ",
        "ặ",
        "ẳ",
        "ẵ",
        "É",
        "È",
        "Ẽ",
        "Ẹ",
        "Ê",
        "Ế",
        "Ề",
        "Ễ",
        "Ệ",
        "è",
        "é",
        "ẹ",
        "ẻ",
        "ẽ",
        "ê",
        "ề",
        "ế",
        "ệ",
        "ể",
        "ễ",
        "Í",
        "Ì",
        "Ĩ",
        "Ị",
        "ì",
        "í",
        "ị",
        "ỉ",
        "ĩ",
        "Ó",
        "Ò",
        "Õ",
        "Ọ",
        "Ô",
        "Ố",
        "Ồ",
        "Ỗ",
        "Ộ",
        "Ơ",
        "Ớ",
        "Ờ",
        "Ỡ",
        "Ợ",
        "ò",
        "ó",
        "ọ",
        "ỏ",
        "õ",
        "ô",
        "ồ",
        "ố",
        "ộ",
        "ổ",
        "ỗ",
        "ơ",
        "ờ",
        "ớ",
        "ợ",
        "ở",
        "ỡ",
        "Ú",
        "Ù",
        "Ũ",
        "Ụ",
        "Ư",
        "Ứ",
        "Ừ",
        "Ữ",
        "Ự",
        "ù",
        "ú",
        "ụ",
        "ủ",
        "ũ",
        "ư",
        "ừ",
        "ứ",
        "ử",
        "ữ",
        "Ý",
        "Ỳ",
        "Ỹ",
        "Ỵ",
        "ỳ",
        "ý",
        "ỵ",
        "ỷ",
        "ỹ",
        "Đ",
        "đ",
    ]
    for char in a_str:
        if char in vnmese_chars:
            return True
    return False



def refine_data(content: str) -> None:
    try:
        index = content.index("@       IN              NS              localhost.\n") + 1
        if content[index] == "\n":
            index += 1
    except:
            index = 0
            
    content = content[index:]
    for i in range(len(content)):
        # process input
        content[i] = content[i].replace("       300           IN             A       116.101.122.171\n","").replace("       300           IN             A       116.101.122.171", "").replace(" ","")
        temp_value = content[i].replace("www.", "")

        # check whether it's an ipv4 or not
        ipv4 = True
        if len(temp_value.split(".")) == 4:
            for char in temp_value:
                if char.isalpha():
                    ipv4 = False
        else:
            ipv4 = False

        if (not ipv4) and (not contains_vnmese_char(temp_value)) and (content[i] not in output_container) :
            output_container.append(content[i])


if __name__ == "__main__":
    for i in range(1, len(sys.argv)):
        flag = sys.argv[i]
        if flag == "-i":
            input_file = sys.argv[i + 1]
            with open(input_file, mode="r", encoding="utf-8") as input:
                content = input.readlines()
                refine_data(content)
                
                with open(f"{output_folder}\\refined_data.txt", mode="w") as output:
                    output.write(
                                "$TTL 1D\n@       IN      SOA     spoof.safegate.vn. safegate.vn. (\n                        2023011101      ; serial\n                        3H              ; refresh\n                        1H              ; retry\n                        3D              ; expire\n                        1H              ; minimum\n                        )\n@       IN              NS              localhost.\n\n"
                            )
                    for item in output_container:
                        output.write(
                                        item
                                        + "       300           IN             A       116.101.122.171\n"
                                    )
    

    