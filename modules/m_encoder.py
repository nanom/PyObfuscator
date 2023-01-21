import base64
import random
import codecs
from typing import List, Tuple, Dict, Any


class Encoder:
    def __init__(
        self, 
        program_vars: List[str],
        encoding_method: str
    ) -> None:

        self.program_struct = {var.strip():{} for var in program_vars if var != ""}
        self.encoding_method = encoding_method

    def __get_chunks_idx(
        self, 
        str: str
    ) -> List[Tuple[int, int]]:

        program_size = len(str) 
        n_chunk = len(self.program_struct)
        chunk_size = int(program_size / n_chunk) 
        idx = []
        for i in range(0, n_chunk*chunk_size, chunk_size):
            e = i + chunk_size
            if e == n_chunk * chunk_size:
                e = program_size
            idx.append((i,e))
        return idx
    
    def __set_program_struct(
        self, 
        var: str, 
        feature: str, 
        value: Any
    ) -> None:

        self.program_struct[var][feature] = value

    def str_to_hex(
        self, 
        str: str
    ) -> str:

        return ''.join([hex(ord(c)).replace('0x','\\x') for c in str])

    def str_to_base64(
        self, 
        str: str
    ) -> str:

        return base64.b64encode(str.encode('utf-8')).decode('utf-8')

    def base64_to_custom_encoding(
        self, 
        str: str
    ) -> str:

        return codecs.encode(str, self.encoding_method)
    
    def execute(
        self, 
        program_str: str
    ) -> Dict:

        # Encode in base65 the original str program
        program_b64 = self.str_to_base64(program_str)

        # Get boundaries to divide the encoded program in len(program_parts) parts
        idx = self.__get_chunks_idx(program_b64)

        for ith, (k,_) in enumerate(self.program_struct.items()):
            current_part = program_b64[ idx[ith][0]:idx[ith][1] ]
            self.__set_program_struct(k,'hex', self.str_to_hex(k))
            self.__set_program_struct(k,'base64_encode', current_part)

            # Re-Encode the current part with a probability of .6, using encoding_method
            if random.random() >= .6:
                self.__set_program_struct(k,'base64_encode', self.base64_to_custom_encoding(current_part))
                self.__set_program_struct(k,self.encoding_method, True)
            else:
                self.__set_program_struct(k,self.encoding_method, False)

        return self.program_struct