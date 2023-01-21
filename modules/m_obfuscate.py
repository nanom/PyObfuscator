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
        encoding_var: str = None,
        execute_var: str = None
    ) -> None:

        self.input_path = input_path
        self.output_dir_path = output_dir_name
        self.program_vars = program_vars
        self.encoding_var = encoding_var
        self.execute_var = execute_var

        # At now, only work with 'rot13' Caesar cipher.
        self.encoding_method = 'rot13'

        self.__all_files_path = None
        self.__py_files_path = None

        self.__check_input_parameters()
        self.__create_output_paths()

    def __check_input_parameters(
        self, 
    ) -> None:

        if not os.path.exists(self.input_path):
            raise Exception(f"Error. The input path '{self.input_path}' doesn't exists!")
        
        if self.output_dir_path is None:
            raise Exception("Error. The parameter 'output_dir_name' can't be empty!")
        
        if self.program_vars is not None:
            # Checking that each name doesn't start with a numeric character.
            all_names_are_correctly = True

            for name in self.program_vars:
                all_names_are_correctly = all_names_are_correctly and name.strip()[0].isalpha()
            
            if not all_names_are_correctly:
                raise Exception("Error: Each variable name in `program_vars` must start with an alphabetic  character!")
        
        if self.encoding_var is None:
            self.encoding_var = self.__gen_name(10)
        
        if self.execute_var is None:
            self.execute_var = self.__gen_name(10)

    def __create_output_paths(
        self
    ) -> None:

        # --- Create output folder ---
        self.output_dir_path = os.path.join(os.getcwd(), self.output_dir_path)
        if os.path.exists(self.output_dir_path):
            shutil.rmtree(self.output_dir_path)
        else:
            os.mkdir(self.output_dir_path)

        # --- Get files path ---
        self.__all_files_path = [self.input_path]
        self.__py_files_path = []

        # 1. Search all files path
        if os.path.isdir(self.input_path):
            self.__all_files_path = []
            directories = self.__recursive_dir_search(self.input_path)
            for d in directories:
                child_list = [os.path.join(d,e) for e in os.listdir(d)]
                self.__all_files_path += [e for e in child_list if os.path.isfile(e)]

        # 2. Store python files path and copy non python files 
        for s_path in self.__all_files_path:

            is_py_file = os.path.splitext(s_path)[-1] == '.py'
            if is_py_file:
                self.__py_files_path.append(s_path)

            d_path = os.path.join(self.output_dir_path, s_path)
            base_dir = os.path.dirname(d_path)
            
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)

            if not os.path.exists(d_path) and not is_py_file:
                shutil.copy(s_path, d_path)

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

    def __get_program_vars(
        self,
        program_size: int
    ) -> List[str]:

        min_n_vars = 1
        max_n_vars = 10

        if self.program_vars is None:
            n = random.randint(min_n_vars, max_n_vars)
            self.program_vars = [
                self.__gen_name()
                for _ in range(0, n) 
                if n < program_size
            ]
        else:
            self.program_vars = [
                var_name.strip() 
                for ith, var_name in enumerate(self.program_vars) 
                if var_name.strip() != "" and ith < program_size
            ]

        return self.program_vars
    
    def __file_to_string(
        self, 
        path: str
    ) -> str:

        str_code = ""
        with open(path, 'r') as f:
            str_code = f.read()
        return str_code

    def __gen_name(
        self, 
        size: int = 6
    ) -> str:

        bag = string.digits + string.ascii_letters
        var_name = \
            random.choice(string.ascii_letters) + \
            ''.join(random.choice(bag) for _ in range(size - 1))
        
        return var_name

    def execute(
        self
    ) -> None:

        for file_path in self.__py_files_path:
            
            p_str = self.__file_to_string(file_path)
            p_size = len(p_str)
            p_vars = self.__get_program_vars(p_size)

            encoder = Encoder(p_vars, self.encoding_method)
            decoder = Decoder(self.output_dir_path, self.encoding_var, self.execute_var)
            
            p_struct = encoder.execute(p_str)
            decoder.execute(file_path, p_struct, self.encoding_method)
            
            print(f"File '{file_path}' ... OK")

        print(f"{len(self.__py_files_path)} files have been successfully obfuscated!")