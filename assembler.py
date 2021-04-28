import logging
import sys

asm_filepath = 'example.asm'
bin_filepath = 'example.hack'
binary = open(bin_filepath, "w")
labels = {}
line_no = 0
logger = logging.getLogger("logger")
logger.setLevel(logging.ERROR)
pureCode = []

compute_values = {"0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100",
                  "A": "0110000", "M": "1110000", "!D": "0001101", "!A": "0110001",
                  "!M": "1110001", "-D": "0001111", "-A": "0110011", "-M": "1110011",
                  "D+1": "0011111", "A+1": "0110111", "M+1": "1110111", "D-1": "0001110",
                  "A-1": "0110010", "M-1": "1110010", "D+A": "0000010", "D+M": "1000010",
                  "M+D": "1000010", "D-A": "0010011", "D-M": "1010011", "A-D": "0000111",
                  "M-D": "1000111", "D&A": "0000000", "D&M": "1000000", "D|A": "0010101",
                  "D|M": "1010101"}

destination_values = {"": "000", "M": "001", "D": "010", "MD": "011", "A": "100",
                      "AM": "101", "AD": "110", "AMD": "111"}

jump_values = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011", "JLT": "100", "JNE": "101",
               "JLE": "110", "JMP": "111"}
variables = {}
variable_address = 16
keywords = {"SCREEN": 0x4000, "KBD": 0x6000, "SP": 0x0000, "LCL": 0x0001, "ARG": 0x0002, "THIS": 0x0003, "THAT": 0x0004}
with open(asm_filepath) as fp:
    for line in fp:

        no_space_line = line.replace(" ", "").replace("\n", "")
        if no_space_line.__contains__("//"):  # remove comments
            starting_char = no_space_line.index("/")
            no_space_line = no_space_line[:starting_char]
        if no_space_line.startswith("(") and no_space_line.endswith(")"):  # find labels and save the line number
            current_label = no_space_line[1:-1]
            labels[current_label] = line_no
            no_space_line = ""

        if no_space_line != "":  # numerate the lines
            # print(str(line_no) + ":" + no_space_line)
            pureCode.append(no_space_line)
            line_no += 1

# print(labels)
# print(pureCode)

line_no = 0
c_command = "111"
for line in pureCode:
    if line.startswith("@"):  # find A command and translate
        value_to_load = line[1:]
        if value_to_load.isnumeric():
            numeric_value = int(value_to_load)
            if numeric_value <= 2 ** 15 - 1:
                temp = "{0:016b}".format(numeric_value)
                binary.write(temp + "\n")
            else:
                logger.error("value you are trying to load {} is too large".format(numeric_value))
                sys.exit(1)
        elif line[1].isalpha() and line[1] == "R":
            if line[2:].isnumeric():
                address = int(line[2:])
                if address <= 15:
                    temp = "{0:016b}".format(address)
                    binary.write(temp + "\n")
                else:
                    logger.error("register {} does not exist".format(address))
                    sys.exit(1)
        elif value_to_load in keywords:
            temp = "{0:016b}".format(keywords[value_to_load])
            binary.write(temp + "\n")

        elif value_to_load in labels:
            temp = "{0:016b}".format(labels[value_to_load])
            binary.write(temp + "\n")
        else:
            if not (value_to_load[0].isnumeric()):
                if value_to_load not in variables:
                    variables[value_to_load] = variable_address
                    variable_address += 1

                temp = "{0:016b}".format(variables[value_to_load])
                binary.write(temp + "\n")

            else:
                logger.error("{} is an illegal name for a variable ".format(value_to_load))
                sys.exit(1)
    elif "=" in line and ";" in line:  # find C command and translate
        destination = line[:line.index("=")].upper()
        if destination in destination_values:
            dest = destination_values[destination]
        else:
            logger.error("{} is an illegal destination value ".format(destination))
            sys.exit(1)

        compute = line[line.index("=") + 1:line.index(";")].upper()
        if compute in compute_values:
            comp = compute_values[compute]
        else:
            logger.error("{} is an illegal compute value ".format(compute))
            sys.exit(1)

        jump = line[line.index(";") + 1:].upper()
        if jump in jump_values:
            jmp = jump_values[jump]
        else:
            logger.error("{} is an illegal jump value ".format(jump))
            sys.exit(1)

        binary.write(c_command + comp + dest + jump + "\n")
    elif "=" in line:
        destination = line[:line.index("=")].upper()
        if destination in destination_values:
            dest = destination_values[destination]
        else:
            logger.error("{} is an illegal destination value ".format(destination))
            sys.exit(1)

        compute = line[line.index("=") + 1:].upper()
        if compute in compute_values:
            comp = compute_values[compute]
        else:
            logger.error("{} is an illegal compute value ".format(compute))
            sys.exit(1)
        binary.write(c_command + comp + dest + "000" + "\n")

    elif ";" in line:
        compute = line[:line.index(";")].upper()
        if compute in compute_values:
            comp = compute_values[compute]
        else:
            logger.error("{} is an illegal compute value ".format(compute))
            sys.exit(1)

        jump = line[line.index(";") + 1:].upper()
        if jump in jump_values:
            jmp = jump_values[jump]
        else:
            logger.error("{} is an illegal jump value ".format(jump))
            sys.exit(1)
        binary.write(c_command + comp + "000" + jmp + "\n")
    line_no += 1

binary.close()
