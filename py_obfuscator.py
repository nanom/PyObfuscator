#!/usr/bin/env python3.9

import argparse
from modules.m_obfuscate import Obfuscate

def getArguments():
    ap = argparse.ArgumentParser(
        prog="./py_obfuscate.py",
        description="PyObfuscator is a basic command line tool that allows you to obfuscate Python code.", 
    )
    ap.add_argument("-i","--input_path", 
        required=True,
        type=str, 
        help="Enter python filename or directory path."
    )
    ap.add_argument("-o","--output_dir", 
        required=False,
        type=str,
        default="output",
        help="Enter an output directory name, where the obfuscated program will be saved. (Default='output')."
    )
    ap.add_argument("-v","--program_vars", 
        required=False,
        type=str,
        help="Enter a list of variable names into which the program will be divided (eg var1, var2, var3). Otherwise, the tool will generate random names for you."
    )

    return vars(ap.parse_args())


if __name__ == '__main__':
    args = getArguments()

    program_vars = args.get('program_vars')
    if program_vars is not None:
        program_vars = [var_name for var_name in program_vars.split(",") if var_name != ""]

    obf = Obfuscate(
        input_path = args.get('input_path'),
        output_dir_name = args.get('output_dir'),
        program_vars = program_vars
    )
    obf.execute()