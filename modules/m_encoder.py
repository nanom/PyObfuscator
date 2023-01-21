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

        self.program_parts = {var.strip():{} for var in program_vars if var != ""}
        self.encoding_method = encoding_method

    def __get_chunk_idxs(
        self, 
        str: str
    ) -> List[Tuple[int, int]]:

        code_size = len(str) 
        chunk = len(self.program_parts)
        chunk_size = int(code_size / chunk) 
        idx = []
        for i in range(0, chunk*chunk_size, chunk_size):
            e = i + chunk_size
            if e == chunk * chunk_size:
                e = code_size
            idx.append((i,e))
        return idx
    
    def __set_program_part(
        self, 
        var: str, 
        feature: str, 
        value: Any
    ) -> None:

        self.program_parts[var][feature] = value

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
        b64_program = self.str_to_base64(program_str)

        # Get boundaries to divide the encoded program in len(program_parts) parts
        idxs = self.__get_chunk_idxs(b64_program)

        for ith, (k,_) in enumerate(self.program_parts.items()):
            current_part = b64_program[ idxs[ith][0]:idxs[ith][1] ]
            self.__set_program_part(k,'hex', self.str_to_hex(k))
            self.__set_program_part(k,'base64_encode', current_part)

            # Re-Encode the current part with a probability of .6, using encoding_method
            if random.random() >= .6:
                self.__set_program_part(k,'base64_encode', self.base64_to_custom_encoding(current_part))
                self.__set_program_part(k,self.encoding_method, True)
            else:
                self.__set_program_part(k,self.encoding_method, False)

        return self.program_parts