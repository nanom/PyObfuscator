import random
import os
import shutil
import string
import sys
from typing import List
from modules.m_encoder import Encoder
from modules.m_decoder import Decoder


class Obfuscate:
    def __init__(
        self, 
        input_path: str,
        output_dir_name: str = None,
        program_vars: List[str] = None
    ) -> None:

        self.input_path = input_path
        self.output_dir_path = output_dir_name
        self.program_vars = program_vars

        # At now, only work with 'rot13' Caesar cipher.
        self.encoding_method = 'rot13'
        self.encoding_var = None
        self.execute_var = None

        self.__all_files_path = None
        self.__py_files_path = None

        self.__check_input_parameters()
        self.__create_output_paths()

    def __check_input_parameters(
        self, 
    ) -> None:

        # --- Checking input path ---
        if not os.path.exists(self.input_path):
            sys.exit(f"Error. The INPUT path '{self.input_path}' doesn't exists!")
        
        # --- Checking output path ---
        if self.output_dir_path is None:
            sys.exit("Error. The parameter 'OUTPUT_DIR_NAME' can't be empty!")
        
        # --- Checking input program_list vars names ---
        if self.program_vars is not None:

            # Checking that each name doesn't start with a numeric character.
            all_names_are_correctly = True

            for name in self.program_vars:
                all_names_are_correctly = all_names_are_correctly and name.strip()[0].isalpha()
            
            if not all_names_are_correctly:
                sys.exit("Error: Variable names entered in `PROGRAM_VARS` parameter must start with an alphabetic character!")

            # Checking that list have at least three names
            if len(self.program_vars) < 3:
                sys.exit("Error: The parameter `PROGRAM_VARS` must be a list of strings with at least three names!")

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
        max_n_vars = 7

        if self.program_vars is None:
            n = random.randint(min_n_vars, max_n_vars)
            
            # Generate list of variables name
            self.program_vars = [
                self.__new_name()
                for _ in range(0, n) 
                if n < program_size
            ]

            # Generate random names to `self.encoding_var` and `self.execute_var`
            self.execute_var = self.__new_name()
            self.encoding_var = self.__new_name()
        else:
            self.program_vars = [
                var_name.strip() 
                for ith, var_name in enumerate(self.program_vars) 
                if var_name.strip() != "" and ith < program_size
            ]

            # Assign the last 2 names of the self.program_vars to `self.encoding_var` and `self.execute_var`
            self.encoding_var = self.program_vars[-2]
            self.execute_var = self.program_vars[-1]
            self.program_vars = self.program_vars[:-2] 

        return self.program_vars
    
    def __file_to_string(
        self, 
        path: str
    ) -> str:

        str_code = ""
        with open(path, 'r') as f:
            str_code = f.read()
        return str_code

    def __new_name(
        self, 
        length: int = 7
    ) -> str:

        bag = string.digits + string.ascii_letters
        var_name = \
            random.choice(string.ascii_letters) + \
            ''.join(random.choice(bag) for _ in range(length - 1))
        
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

        print(f"The files have been successfully obfuscated in '{self.output_dir_path}' !")