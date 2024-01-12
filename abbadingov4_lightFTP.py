import glob
import os

def swap_file_name(filename):
    valid_suffixes = ["c1", "c2", "c3", "c4"]

    if not any(filename.endswith(suffix) for suffix in valid_suffixes):
        parts = filename.split("-")
        if len(parts) == 2:
            src, dst = parts
            src_ip, src_port = src.split('.',1)
            dst_ip, dst_port = dst.split('.',1)
            new_filename = f"{dst_ip}.{dst_port}-{src_ip}.{src_port}"
            return new_filename
        else:
            return None

    for suffix in valid_suffixes:
        if filename.endswith(suffix):
            parts = filename.replace(suffix, "").split("-")
            if len(parts) == 2:
                src, dst = parts
                src_ip, src_port = src.split('.', 1)
                dst_ip, dst_port = dst.split('.', 1)
                new_filename = f"{dst_ip}.{dst_port}-{src_ip}.{src_port}{suffix}"
                return new_filename

    return None


def remove_unnecessary_response_codes(lines, prefixes):
    return [line for line in lines if not any(line.startswith(prefix) for prefix in prefixes)]


FTP_COMMANDS_DICT = {
    "INITIAL": -1,
    "USER_OK": 0,
    "USER_FAULT":0,
    "QUIT": 1,
    "NOOP": 2,
    "PWD":  3,
    "TYPE": 4,
    "PORT": 5,
    "LIST": 6,
    "CDUP": 7,
    "CWD":  8,
    "RETR": 9,
    "ABOR": 10,
    "DELE": 11,
    "PASV": 12,
    "PASS_OK": 13,
    "PASS_FAULT":13,
    "REST": 14,
    "SIZE": 15,
    "MKD":  16,
    "RMD":  17,
    "STOR": 18,
    "SYST": 19,
    "FEAT": 20,
    "APPE": 21,
    "RNFR": 22,
    "RNTO": 23,
    "OPTS": 24,
    "MLSD": 25,
    "AUTH": 26,
    "PBSZ": 27,
    "PROT": 28,
    "EPSV": 29,
    "HELP": 30,
    "SITE": 31,
    "UNKNOWN": 32,
}

def abstraction_function(line, swap_line, isCorrectUser):
    '''
    Strips the input and output traces of text and checks if the username and/or password are correct.
    '''
    try: 
        word_line = line.split()[0]

    except:
        word_line = "500"
    try:
        swap_line = swap_line.split()
        
    except:
        swap_line = ["UNKNOWN", "", ""]

    word_swap_line = "UNKNOWN"

    if len(swap_line) >= 1:
        if swap_line[0] == "USER":
            isCorrectUser = swap_line[1] == "ubuntu" or swap_line[1] == "anonymous" if len(swap_line) > 1 else False
            word_swap_line = "USER_OK" if isCorrectUser else "USER_FAULT"
        elif swap_line[0] == "PASS":
            isCorrectPass = swap_line[1] == "ubuntu" if len(swap_line) > 1 else False
            word_swap_line = "PASS_OK" if isCorrectPass and isCorrectUser else "PASS_FAULT"
        else:
            word_swap_line = swap_line[0]

    if not word_swap_line in FTP_COMMANDS_DICT:
        word_swap_line = "UNKNOWN"

    return word_line, word_swap_line, isCorrectUser

def text_to_abbadingo(word_line, word_swap_line, string, different_combinations, check):
    '''
    Transforms the different client commands of the input trace and the server response of the output trace to abbadingo format.
    '''
    if word_line.isdigit():
        check += 1
        string += f" {word_swap_line}/{word_line}"
        combination = f"{word_swap_line}/{word_line}"
        different_combinations.add(combination)
    return string, different_combinations, check



def main(path):

    all_files = glob.glob(f"{path}/*")

    different_combinations = set()

    number_of_useful_files = 0

    #create a new file where the abbadingo file will be written in
    with open("lightftp9jan.dat", "w") as abbadingo:
        # Go over every file in the folder
        for file_path in all_files:
            if file_path.startswith(f"{path}/127.000.000.001.02200"):
                # Store the input and output trace file name
                file_name = file_path.split("/")[-1]
                swap_name = swap_file_name(file_name)
                if os.path.exists(file_path) and os.path.exists(f"{path}/{swap_name}"):
                    with open(file_path, 'r', encoding='latin1') as file, open(f"{path}/{swap_name}", 'r', encoding='latin1') as swap_file:
                        # Read the input and output trace contents and remove the unnecessary response codes
                        lines = file.readlines()
                        lines = remove_unnecessary_response_codes(lines, ["150", "220", "214"])
                        swap_lines = swap_file.readlines()
                        
                        
                        if len(lines) == len(swap_lines):
                            # Add the label and length of the trace for Abbadingo format
                            length = len(swap_lines)
                            
                            string = f"A {length}"
                            # Set variable isCorrectUser, true if the trace contains "USER ubuntu"
                            isCorrectUser = False
                            # Set variable check, check if the length is the same as the amount of input/output pars
                            check = 0

                            for line, swap_line in zip(lines, swap_lines):
                                word_line, word_swap_line, isCorrectUser = abstraction_function(line, swap_line, isCorrectUser)
                                string, different_combinations, check = text_to_abbadingo(word_line, word_swap_line, string, different_combinations, check)

                            if check == length:
                                abbadingo.write(string + "\n")
                                number_of_useful_files += 1
        abbadingo.seek(0)
        length_combinations = len(different_combinations)
        abbadingo.write(f"{number_of_useful_files} {length_combinations}\n")

if __name__ == "__main__":
    path = "/flow_lightftp"
    main(path)