import logging
import sys
import argparse
import os

parser = argparse.ArgumentParser(description='convert vm language to hack assembly language')
parser.add_argument('filename', default="BasicTest", type=str, help='vm file name')
args = parser.parse_args()
folder_dir = 'D:\\chrome_downloads\\nand2tetris\\nand2tetris\\projects\\07\\MemoryAccess'   #os.getcwd()
to_translate = os.path.join(folder_dir, args.filename)


data_types_dynamic_locations = {'temp': "5"}
data_types_base_address = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': "THAT"}
pointer_types = ['THIS', 'THAT']

arithmetic_commands = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']

logging.basicConfig()
logger = logging.getLogger("logger")
logger.setLevel(logging.ERROR)

logger.error("current dir is {}".format(folder_dir))

def parse_command(vm_command, vm_command_line):
    vm_data_segment = ''
    vm_data_segment_index = ''
    if ' ' not in vm_command:  # check if primitive function
        vm_command_type = vm_command
    else:
        vm_command_type = vm_command[:vm_command.index(" ")]
        data = vm_command[vm_command.index(" ") + 1:]

        if ' ' in data:
            vm_data_segment = data[:data.index(' ')]
            vm_data_segment_index = data[data.index(' ') + 1:]

        else:
            logger.error("{} in line {} is an illegal command ".format(vm_command, vm_command_line))
            sys.exit(1)

    return [vm_command_type, vm_data_segment, vm_data_segment_index]


def push_conversion(segment_data, vm_command_line):
    segment_type = segment_data[0]
    segment_index = segment_data[1]
    if segment_type == 'constant':
        hack_commands = ['@' + segment_index, 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1', ]
    elif segment_type in data_types_base_address:
        hack_commands = ['@' + segment_index, 'D=A', '@' + data_types_base_address[segment_type], 'A=M', 'A=A+D',
                         'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif segment_type in data_types_dynamic_locations:
        if segment_type == 'temp':
            if int(segment_index) < 0 or int(segment_index) > 7:
                logger.error("{} command line is an exceeding range of temp segment".format(vm_command_line))
                sys.exit(1)
        hack_commands = ['@' + segment_index, 'D=A', '@' + data_types_dynamic_locations[segment_type], 'A=D+A',
                         'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif segment_type == 'static':
        if int(segment_index) < 0 or int(segment_index) > 239:
            logger.error("command in line {} is an exceeding range of static segment".format(vm_command_line))
            sys.exit(1)
        hack_commands = ['@' + args.filename + '.' + segment_index, 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif segment_type == 'pointer':
        if segment_index == '0' or segment_index == '1':
            hack_commands = ['@' + pointer_types[int(segment_index)], 'D=M', '@SP', 'A=M', 'M=D', "@SP", "M=M+1"]
        else:
            logger.error("Illegal index {} for pointer in line {}".format(segment_index, vm_command_line))
            sys.exit(1)
    else:
        logger.error("command in line {} has unknown data segment {}".format(vm_command_line, segment_type))
        sys.exit(1)
    return hack_commands


def pop_conversion(segment_data, vm_command_line):
    segment_type = segment_data[0]
    segment_index = segment_data[1]
    if segment_type in data_types_base_address:
        hack_commands = ['@' + data_types_base_address[segment_type], 'D=M', '@' + segment_index, 'D=A+D',
                         '@SP', 'A=M', 'M=D', 'A=A-1', 'D=M', 'A=A+1', 'A=M', 'M=D', '@SP', 'M=M-1']
    elif segment_type in data_types_dynamic_locations:
        if segment_type == 'temp':
            if int(segment_index) < 0 or int(segment_index) > 7:
                logger.error("{} command line is an exceeding range of temp segment".format(vm_command_line))
                sys.exit(1)
        hack_commands = ['@' + data_types_dynamic_locations[segment_type], 'D=A', '@' + segment_index, 'D=A+D',
                         '@SP', 'A=M', 'M=D', 'A=A-1', 'D=M', 'A=A+1', 'A=M', 'M=D', '@SP', 'M=M-1']
    elif segment_type == 'static':
        if int(segment_index) < 0 or int(segment_index) > 239:
            logger.error("command in line {} is an exceeding range of static segment".format(vm_command_line))
            sys.exit(1)
        hack_commands = ['@SP', 'M=M-1', 'A=M', 'D=M', '@' + args.filename + '.' + segment_index, 'M=D']
    elif segment_type == 'pointer':
        if segment_index == '0' or segment_index == '1':
            hack_commands = ['@SP', 'M=M-1', 'A=M', 'D=M', '@' + pointer_types[int(segment_index)], 'M=D']
        else:
            logger.error("Illegal index {} for pointer in line {}".format(segment_index, vm_command_line))
            sys.exit(1)
    else:
        logger.error("command in line {} has unknown data segment {}".format(vm_command_line, segment_type))
        sys.exit(1)
    return hack_commands


def add_conversion():
    hack_commands = ["@SP", "M=M-1", 'A=M', "D=M", "@SP", "M=M-1", "A=M", "M=D+M", "@SP", 'M=M+1']
    return hack_commands


def sub_conversion():
    hack_commands = ['@SP', 'M=M-1', 'A=M', 'D=M', '@SP', 'M=M-1', 'A=M', 'M=M-D', '@SP', 'M=M+1']
    return hack_commands


def neg_conversion():
    hack_commands = ["@SP", 'M=M-1', "A=M", "M=-M", '@SP', 'M=M+1']
    return hack_commands


def eq_conversion(label_index):
    hack_commands = ['@SP', 'M=M-1', 'A=M', 'D=M', '@SP', 'M=M-1', 'A=M', 'D=D-M',
                     '@' + args.filename + '.' + 'JUMP' + str(label_index), 'D;JEQ', 'D=-1',
                     '(' + args.filename + '.' + 'JUMP' + str(label_index) + ')', '@SP', 'A=M', 'M=!D', '@SP', 'M=M+1']
    return hack_commands


def gt_conversion(label_index):
    hack_commands = ['@SP', 'M=M-1', 'A=M', 'D=M', '@SP', 'M=M-1', 'A=M', 'D=M-D',
                     '@' + args.filename + '.' + 'JUMP' + str(label_index), 'D;JGT', 'D=0',
                     '@' + args.filename + '.' + 'END' + str(label_index), '0;JMP',
                     '(' + args.filename + '.' + 'JUMP' + str(label_index) + ')', 'D=-1',
                     '(' + args.filename + '.' + 'END' + str(label_index) + ')', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    return hack_commands


def lt_conversion(label_index):
    hack_commands = ['@SP', 'M=M-1', 'A=M', 'D=M', '@SP', 'M=M-1', 'A=M', 'D=M-D',
                     '@' + args.filename + '.' + 'JUMP' + str(label_index), 'D;JLT', 'D=0',
                     '@' + args.filename + '.' + 'END' + str(label_index), '0;JMP',
                     '(' + args.filename + '.' + 'JUMP' + str(label_index) + ')', 'D=-1',
                     '(' + args.filename + '.' + 'END' + str(label_index) + ')', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    return hack_commands


def and_conversion():
    hack_commands = ["@SP", 'M=M-1', "A=M", "D=M", "@SP", "M=M-1", "A=M", "M=D&M", "@SP", 'M=M+1']
    return hack_commands


def or_conversion():
    hack_commands = ["@SP", 'M=M-1', "A=M", "D=M", "@SP", "M=M-1", "A=M", "M=D|M", "@SP", 'M=M+1']
    return hack_commands


def not_conversion():
    hack_commands = ["@SP", 'M=M-1', "A=M", "M=!M", '@SP', 'M=M+1']
    return hack_commands


def choose_action(parsed_command, vm_command_line, label_index):
    command_type = parsed_command[0]
    if command_type in arithmetic_commands:
        if command_type == 'add':
            write_hack_to_file(add_conversion())
        elif command_type == 'sub':
            write_hack_to_file(sub_conversion())
        elif command_type == 'neg':
            write_hack_to_file(neg_conversion())
        elif command_type == 'eq':
            write_hack_to_file(eq_conversion(label_index))
            label_index += 1
        elif command_type == 'gt':
            write_hack_to_file(gt_conversion(label_index))
            label_index += 1
        elif command_type == 'lt':
            write_hack_to_file(lt_conversion(label_index))
            label_index += 1
        elif command_type == 'and':
            write_hack_to_file(and_conversion())
        elif command_type == 'or':
            write_hack_to_file(or_conversion())
        elif command_type == 'not':
            write_hack_to_file(not_conversion())
    elif command_type == 'push':
        write_hack_to_file(push_conversion(parsed_command[1:], vm_command_line))
    elif command_type == 'pop':
        write_hack_to_file(pop_conversion(parsed_command[1:], vm_command_line))
    else:
        logger.error("{} command type in line {} is an illegal command type "
                     .format(parsed_command[0], vm_command_line))
        sys.exit(1)
    return label_index


def write_hack_to_file(hack_commands):
    for hack_command in hack_commands:
        hack.write(hack_command + "\n")


def open_file(vm_file):
    with open(vm_file) as fp:
        commented_code = ''
        jump_label_index = 0
        for count, line in enumerate(fp):
            pure_code = line.replace("\n", "")
            if pure_code.__contains__("//"):  # remove comments
                starting_char = pure_code.index("/")
                pure_code = pure_code[:starting_char]
            if pure_code != '':
                commented_code = "// " + pure_code + "\n"
                hack.write(commented_code)
                jump_label_index = choose_action(parse_command(pure_code, count), count, jump_label_index)


if os.path.isdir(to_translate):
    os.chdir(to_translate)
    hack_filename = os.path.basename(to_translate) + '.asm'
    hack = open(hack_filename, "w")
    for file in os.listdir(to_translate):
        temp = os.path.splitext(file)
        if '.vm' == os.path.splitext(file)[1]:
            args.filename = os.path.splitext(os.path.basename(args.filename))[0]
            open_file(os.path.join(to_translate, file))
elif os.path.isfile(to_translate):
    args.filename = os.path.splitext(os.path.basename(args.filename))[0]  # remove file type
    vm_filepath = os.path.splitext(to_translate)[0] + '.vm'
    hack_filename = os.path.splitext(to_translate)[0] + '.asm'
    hack = open(hack_filename, "w")
    open_file(vm_filepath)
else:
    logger.error("file/folder {} does not exist ".format(to_translate))
    sys.exit(1)

hack.close()
logger.error("hack dir is {}".format(hack_filename))
