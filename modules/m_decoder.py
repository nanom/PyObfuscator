import os
from typing import Dict, Any


class Decoder:
    def __init__(
        self,
        output_dir_path: str,
        encoding_var: str,
        execute_var: str
    ) -> None:

        self.output_dir_path = output_dir_path
        self.encoding_var = encoding_var
        self.execute_var = execute_var
        self.program_struct = None

    def __write(
        self, 
        file_path: str, 
        value: str
    ) -> None:

        d_path = os.path.join(self.output_dir_path, file_path)

        with open(d_path, 'a+') as f:
            f.write(value)

    def __get_program_struct(
        self, 
        var: str, 
        feature: str
    ) -> Any:

        return self.program_struct[var][feature]

    def str_to_hex(
        self, 
        str: str
    ) -> str:

        return ''.join([hex(ord(c)).replace('0x','\\x') for c in str])

    def execute(
        self, 
        file_path: str,
        program_struct: Dict,
        encoding_method: str
    ) -> None:

        # Set program_struct as class vars
        self.program_struct = program_struct

        # Write the necessary libraries
        self.__write(
            file_path, 
            "import base64, codecs \n"
        )

        # Write the encoding program's parts
        for k, _ in program_struct.items():
            encode_part = self.__get_program_struct(k, 'base64_encode')
            to_write = f"{k} = '{encode_part}'\n"
            self.__write(file_path, to_write)

        # Write custom encoding method var
        hex_name = self.str_to_hex(encoding_method)
        to_write = f"{self.encoding_var} = '{hex_name}' \n"
        self.__write( file_path, to_write)

        # Write encoding program var
        to_write = f"{self.execute_var} = \\\n"
        for ith, (k,v) in enumerate(program_struct.items()):
            if v[encoding_method]:
                cmd = f"codecs.decode({k},{self.encoding_var})"
                hex_cmd = self.str_to_hex(cmd)
                to_write += f"\teval('{hex_cmd}')"
            else:
                to_write += f"\teval('{v['hex']}')"
            
            if ith != len(program_struct) - 1:
                to_write += f" + \\\n"
        
        self.__write(file_path, to_write)

        # Write cmd to decode program
        hex_name = self.str_to_hex(self.execute_var)
        cmd = f"base64.b64decode(eval('{hex_name}')).decode('utf-8')"
        to_write = f"\neval(compile({cmd},'<app>', 'exec'))"
        self.__write(file_path, to_write)