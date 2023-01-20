#!/usr/bin/env python3.9

import base64
import math
import random
import codecs
import os
import shutil
import argparse
from typing import List, Tuple, Dict, Any

class Obfuscate:
    def __init__(
        self, 
        input_path: str,
        output_dir_name:str = None,
        content_vars:List[str] = ['this', 'is_', 'an', 'simple', 'python','app'],
    ) -> None:

        assert(output_dir_name is not None), "Error the 'output_dir_name' is empty!"
        self.out_dir_path = os.path.join(os.getcwd(), output_dir_name)

        self.content_vars = content_vars
        self.program_var = "code"
        self.encoding_var = "encode"

        # At now, only work with 'rot13' Caesar cipher.
        self.encoding_method = 'rot13'

        self.__all_files_path = None
        self.__py_files_path = None
        self.__check_input_path(input_path)
        self.__create_output_paths()

    def __create_output_paths(
        self
    ) -> None:

        if os.path.exists(self.out_dir_path):
            raise Exception(f"The '{self.out_dir_path}' alredy exist!")

        # Create parent output dir
        os.mkdir(self.out_dir_path)

        # Init python file paths list
        self.__py_files_path = []

        # Copy non-python files and create directory tree
        for s_path in self.__all_files_path:

            is_py_file = os.path.splitext(s_path)[-1] == '.py'
            if is_py_file:
                self.__py_files_path.append(s_path)

            d_path = os.path.join(self.out_dir_path, s_path)
            base_dir = os.path.dirname(d_path)
            
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)

            if not os.path.exists(d_path) and not is_py_file:
                # Copy file form 's_path' to 'd_path'
                shutil.copy(s_path, d_path)

    def __check_input_path(
        self, 
        input_path: str
    ) -> None:

        if not os.path.exists(input_path):
            raise Exception(f"Error. The input path '{input_path}' doesn't exists!")

        self.__all_files_path = [input_path]

        if os.path.isdir(input_path):
            self.__all_files_path = []
            directories = self.__recursive_dir_search(input_path)
            for d in directories:
                child_list = [os.path.join(d,e) for e in os.listdir(d)]
                self.__all_files_path += [e for e in child_list if os.path.isfile(e)]

    def __recursive_dir_search(
        self, 
        root: str
    ) -> List[str]:

        stack = [root]
        visited = []
        while stack:
            parent = stack.pop()
            if parent not in visited:
                visited.append(parent)
                for child in os.listdir(parent):
                    is_hidden = child.startswith('.')
                    is_cache = child.startswith('__')
                    child = os.path.join(parent, child)
                    if os.path.isdir(child) and not (is_hidden or is_cache):
                        stack.append(child)
        return visited
    
    def file_to_string(
        self, 
        path:str
    ) -> str:

        str_code = ""
        with open(path, 'r') as f:
            str_code = f.read()
        return str_code

    def execute(
        self
    ) -> None:

        encoder = Encoder(
            content_vars=self.content_vars,
            encoding_method=self.encoding_method
        )
        decoder = Decoder(
            out_dir_path=self.out_dir_path,
            encoding_var=self.encoding_var,
            program_var=self.program_var
        )

        for file_path in self.__py_files_path:
            print(f"File '{file_path}' ... OK")
            program_str = self.file_to_string(file_path)
            program_parts = encoder.execute(program_str)
            decoder.execute(
                file_path, 
                program_parts, 
                encoder.encoding_method
            )

        print(f"{len(self.__py_files_path)} files have been successfully obfuscated!")

class Encoder:
    def __init__(
        self, 
        content_vars:List[str],
        encoding_method:str
    ) -> None:

        self.program_parts = {var.strip():{} for var in content_vars if var}
        self.encoding_method = encoding_method

    def __get_chunk_idxs(
        self, 
        string:str
    ) -> List[Tuple[int, int]]:

        size_code = len(string) 
        n_chunk = len(self.program_parts)
        size_chunk = math.ceil(size_code / n_chunk ) 
        return [(i, i+size_chunk) for i in range(0, size_code, size_chunk)]
    
    def __set_program_part(
        self, 
        var:str, 
        feature:str, 
        value:Any
    ) -> None:

        self.program_parts[var][feature] = value

    def str_to_hex(
        self, 
        string: str
    ) -> str:

        return ''.join([hex(ord(c)).replace('0x','\\x') for c in string])

    def str_to_base64(
        self, 
        string: str
    ) -> str:

        return base64.b64encode(string.encode('utf-8')).decode('utf-8')

    def base64_to_custom_encoding(
        self, 
        string:str
    ) -> str:

        return codecs.encode(string, self.encoding_method)
    
    def execute(
        self, 
        program_str:str
    ) -> Dict:

        # Encode in base65 the original string program
        b64_program = self.str_to_base64(program_str)

        # Get boundaries to divide the encoded program in len(program_parts) parts
        idxs = self.__get_chunk_idxs(b64_program)

        for ith,(k,_) in enumerate(self.program_parts.items()):
            current_part = b64_program[ idxs[ith][0]:idxs[ith][1] ]
            self.__set_program_part(k,'hex', self.str_to_hex(k))
            self.__set_program_part(k,'base64_encode', current_part)

            # Re-Encode the current part with a probability of .6, using encoding_method
            if random.random() >= .6:
                self.__set_program_part(k, 'base64_encode', self.base64_to_custom_encoding(current_part))
                self.__set_program_part(k, self.encoding_method, True)
            else:
                self.__set_program_part(k, self.encoding_method, False)
        
        return self.program_parts

class Decoder:
    def __init__(
        self,
        out_dir_path:str,
        encoding_var:str,
        program_var:str
    ) -> None:

        self.out_dir_path = out_dir_path
        self.encoding_var = encoding_var
        self.program_var = program_var
        self.program_parts = None

    def __write(
        self, 
        file_path:str, 
        value:str
    ) -> None:

        d_path = os.path.join(self.out_dir_path, file_path)

        with open(d_path, 'a+') as f:
            f.write(value)

    def __get_program_part(
        self, 
        var:str, 
        feature:str
    ) -> Any:

        return self.program_parts[var][feature]

    def str_to_hex(
        self, 
        string: str
    ) -> str:

        return ''.join([hex(ord(c)).replace('0x','\\x') for c in string])

    def execute(
        self, 
        file_path:str,
        program_parts:Dict,
        encoding_method:str
    ) -> None:

        # Set program_parts as class vars
        self.program_parts = program_parts

        # Write the necessary libraries
        self.__write(
            file_path, 
            "import base64, codecs \n"
        )

        # Write the encoding program's parts
        for k, _ in program_parts.items():
            encode_part = self.__get_program_part(k, 'base64_encode')
            to_write = f"{k} = '{encode_part}'\n"
            self.__write(file_path, to_write)

        # Write custom encoding method var
        hex_name = self.str_to_hex(encoding_method)
        to_write = f"{self.encoding_var} = '{hex_name}' \n"
        self.__write( file_path, to_write)

        # Write encoding program var
        to_write = f"{self.program_var} = \\\n"
        for ith, (k,v) in enumerate(program_parts.items()):
            if v[encoding_method]:
                cmd = f"codecs.decode({k},{self.encoding_var})"
                hex_cmd = self.str_to_hex(cmd)
                to_write += f"\teval('{hex_cmd}')"
            else:
                to_write += f"\teval('{v['hex']}')"
            
            if ith != len(program_parts) - 1:
                to_write += f" + \\\n"
        
        self.__write(file_path, to_write)

        # Write cmd to decode program
        hex_name = self.str_to_hex(self.program_var)
        cmd = f"base64.b64decode(eval('{hex_name}')).decode('utf-8')"
        to_write = f"\neval(compile({cmd},'<app>', 'exec'))"
        self.__write(file_path, to_write)

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
    ap.add_argument("-v","--content_vars", 
        required=False,
        type=str,
        default="this, is_, an, simple, python, app",
        help="Enter list of variables in which the program will be partitioned.(Default='this, is_, an, simple, python, app')"
    )

    return vars(ap.parse_args())


if __name__ == '__main__':
    args = getArguments()
    obf = Obfuscate(
        input_path = args['input_path'],
        output_dir_name = args['output_dir'],
        content_vars = [v.strip() for v in args['content_vars'].split(',') if v != ""]
    )
    obf.execute()