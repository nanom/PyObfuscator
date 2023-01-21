import random
import os
import shutil
import string
from typing import List
from modules.m_decoder import Decoder
from modules.m_encoder import Encoder


class Obfuscate:
    def __init__(
        self, 
        input_path: str,
        output_dir_name: str = None,
        program_vars: List[str] = None,
    ) -> None:

        self.out_dir_path = output_dir_name
        self.program_vars = program_vars
        self.encoding_var = "encode"
        self.execute_var = "code"

        # At now, only work with 'rot13' Caesar cipher.
        self.encoding_method = 'rot13'

        self.__all_files_path = None
        self.__py_files_path = None

        self.__check_input_path(input_path)
        self.__create_output_paths()

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
                
    def __create_output_paths(
        self
    ) -> None:

        assert(self.out_dir_path is not None), "Error. The 'output_dir_name' can't be empty!"
        self.out_dir_path = os.path.join(os.getcwd(), self.out_dir_path)

        if os.path.exists(self.out_dir_path):
            shutil.rmtree(self.out_dir_path)
            # raise Exception(f"The '{self.out_dir_path}' alredy exist!")

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
    
    def __gen_new_var_name(
        self, 
        size: int = 6
    ) -> str:

        bag = string.digits + string.ascii_letters
        var_name = random.choice(string.ascii_letters) + ''.join(random.choice(bag) for _ in range(size - 1))
        return var_name

    def __get_program_vars(
        self,
        program_size: int
    ) -> List[str]:

        min_vars_availables = 1
        max_vars_availables = 15

        if self.program_vars is None:
                n = random.randint(min_vars_availables, max_vars_availables + 1)
                self.program_vars = [
                    self.__gen_new_var_name()
                    for _ in range(0, n) 
                    if n < program_size
                ]
        else:
            # Checking that each vars does not start with a numeric character
            all_vars_starts_correctly = True
            for var_name in self.program_vars:
                all_vars_starts_correctly = all_vars_starts_correctly and var_name.strip()[0].isalpha()

            if all_vars_starts_correctly:
                self.program_vars = [
                    var_name.strip() 
                    for ith, var_name in enumerate(self.program_vars) 
                    if var_name.strip() != "" and ith < program_size
                ]

            else:
                raise Exception("Error: The name of ecah variable name in `program_vars` must start with a alphabetic caracter!")
        
        return self.program_vars

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
        path: str
    ) -> str:

        str_code = ""
        with open(path, 'r') as f:
            str_code = f.read()
        return str_code

    def execute(
        self
    ) -> None:

        for file_path in self.__py_files_path:
            
            program_str = self.file_to_string(file_path)
            encoder = Encoder(
                program_vars=self.__get_program_vars(len(program_str)),
                encoding_method=self.encoding_method
            )
            
            program_parts = encoder.execute(program_str)
            decoder = Decoder(
                out_dir_path=self.out_dir_path,
                encoding_var=self.encoding_var,
                execute_var=self.execute_var
            )
            decoder.execute(
                file_path, 
                program_parts, 
                encoder.encoding_method
            )
            print(f"File '{file_path}' ... OK")

        print(f"{len(self.__py_files_path)} files have been successfully obfuscated!")