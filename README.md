# PyObfuscator

## Description
PyObfuscator is a basic command line tool that allows you to obfuscate not just a simple Python script, but also entire programs recursively. This tool is based on base64 encoding and random re-encode of some parts of the code using some an choiced method of the `codecs` library. It also performs transformations of variable names and specific commands to hexadecimal strings.

> **Background:** Obfuscation is the act of creating source code that is difficult for humans to understand. Many times the code is obfuscated to protect intellectual property or trade secrets, and on other occasions to not lose control of our code, avoiding accidental modifications that could break it.
The obfuscation technique, unlike code encryption, allows the program to continue running, without the need for a prior decryption procedure.

## Installation
```bash
# --- 1. Clone this repo ---
$ git clone https://github.com/nanom/PyObfuscator.git && cd PyObfuscator 

# --- 2. Give execute permissions to script ---
$ sudo chmod +x py_ofuscator.py

# --- 3. Create symlink to '/usr/local/bin' so the tool can be used from anywhere ---
$ sudo ln -s <you_absolute_path>/py_ofuscator.py /usr/local/bin/.
```
## How to use
```shell
usage: ./py_obfuscate.py [-h] -i INPUT_PATH [-o OUTPUT_DIR] [-v CONTENT_VARS] [-e ENCODING_METHOD]

PyObfuscator is a basic command line tool that allows you to obfuscate Python code.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_PATH, --input_path INPUT_PATH
                        Enter python filename or directory path.
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Enter an output directory name, where the obfuscated program will be saved. (Default='output').
  -v CONTENT_VARS, --content_vars CONTENT_VARS
                        Enter list of variables in which the program will be partitioned.(Default='this, is_, an, simple,
                        python, app')
  -e ENCODING_METHOD, --encoding_method ENCODING_METHOD
                        Name of the method used to re-encode the content of some content_vars via the codecs py-library.
                        (Default='rot13')
```

## Examples of use
#### Execute the tool to obfuscate `test.py` python file. 
```bash
$ ./py_obfuscate.py -i test.py -o out
```
#### *Input file:*
```python
# test.py
print("Hello World!")
```

#### *Output file:*
```python
# out/test.py
import base64, codecs 
this = 'pUWco'
is_ = 'nQoIk'
an = 'hlbGx'
simple = 'iVSqi'
python = 'pzkxV'
app = 'ik='
encode = '\x72\x6f\x74\x31\x33' 
code = \
    eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x74\x68\x69\x73\x2c\x65\x6e\x63\x6f\x64\x65\x29') + \
    eval('\x69\x73\x5f') + \
    eval('\x61\x6e') + \
    eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x73\x69\x6d\x70\x6c\x65\x2c\x65\x6e\x63\x6f\x64\x65\x29') + \
    eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x70\x79\x74\x68\x6f\x6e\x2c\x65\x6e\x63\x6f\x64\x65\x29') + \
    eval('\x61\x70\x70')
eval(compile(base64.b64decode(eval('\x63\x6f\x64\x65')).decode('utf-8'),'<app>', 'exec'))
```

## Deobfuscation: Reverse Engineering
1. The original code is partitioned and encoded in `base64` between the variables **`this`**, **`is_`** ,**`an`** ,**`simple`** ,**`python`**, and **`app`**. (These variables can be set via the **--content_vars** command line parameter.)
```python
this = 'pUWco'
is_ = 'nQoIk'
an = 'hlbGx'
simple = 'iVSqi'
python = 'pzkxV'
app = 'ik='
```
2. The variable **`encode`** contains the name of the encoding method (in hexadecimal string) used to re-encode the content of some above variables, with a probability of .6. (This method can also be configured via the **--encoding_method** command line parameter.)
```python
encode = '\x72\x6f\x74\x31\x33' 
```
3. The last variable **`code`**, contains the concatenation of the results of several calls to `eval()`. Each of the inputs to `eval()` are encoded in hexadecimal string.  Specifically the actual decoded arguments are:
```python
code = \
    eval(codecs.decode(this, encode)) + \
    eval(is_) + \
    eval(an) + \
    eval(codecs.decode(simple, encode)) + \
    eval(codecs.decode(python, encode)) + \
    eval(app)
```

4. The final content of the **`code`** variable is a base64-encoded string. This is finally decoded using the `base64.b64decode()` command, compiled, and evaluated.
```python
eval(compile(base64.b64decode(eval('\x63\x6f\x64\x65')).decode('utf-8'),'<app>', 'exec'))
```
