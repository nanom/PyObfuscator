# PyObfuscator

## Description.
PyObfuscator is a basic command line tool that allows you to obfuscate not just a simple Python script, but also entire programs recursively. This tool is based on base64 encoding and random re-encode of some parts of the code using the 'Rot13' [Caesar cipher](https://en.wikipedia.org/wiki/ROT13), an encode method include in the `codecs` library. It also performs transformations of variable names and specific commands to hexadecimal strings.

> **Background:** Obfuscation is the act of creating source code that is difficult for humans to understand. Many times the code is obfuscated to protect intellectual property or trade secrets, and on other occasions to not lose control of our code, avoiding accidental modifications that could break it.
The obfuscation technique, unlike code encryption, allows the program to continue running, without the need for a prior decryption procedure.

## Installation.
```bash
# --- 1. Clone this repo ---
$ git clone https://github.com/nanom/PyObfuscator.git && cd PyObfuscator 

# --- 2. Give execute permissions to script ---
$ sudo chmod +x py_ofuscator.py

# --- 3. Create symlink to '/usr/local/bin' so the tool can be used from anywhere ---
$ sudo ln -s <you_absolute_path>/py_ofuscator.py /usr/local/bin/.
```
## How to use.
```shell
usage: ./py_obfuscator.py [-h] -i INPUT_PATH [-o OUTPUT_DIR] [-v PROGRAM_VARS]

PyObfuscator is a basic command line tool that allows you to obfuscate Python code.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Name of te output directory where the obfuscated program will be saved (default: output).
  -v PROGRAM_VARS, --program_vars PROGRAM_VARS
                        Please list at least three variable names where the program will be split (eg: n1,n2,n3,...,nN).
                        Otherwise, random names will be generated for you.

required arguments:
  -i INPUT_PATH, --input_path INPUT_PATH
                        Python filename or program directory name.
```

## Examples of use.
### 1. Using list of variable names entered by the user.

* #### Execute the below command to obfuscate the `test.py` file.
```bash
$ ./py_obfuscator.py \
    -i test.py  \
    -o out \
    -v this,is_,a,simple,coded,python,app
```
* #### *Input file:*
```python
# test.py
print("Hello World!")
```

* #### *Output file:*
```python
# out/test.py
import base64, codecs 
this = 'cHJpb'
is_ = 'aDbVx'
a = 'hlbGx'
simple = 'vIFdv'
coded = 'pzkxVFVc'
python = '\x72\x6f\x74\x31\x33' 
app = \
	eval('\x74\x68\x69\x73') + \
	eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x69\x73\x5f\x2c\x70\x79\x74\x68\x6f\x6e\x29') + \
	eval('\x61') + \
	eval('\x73\x69\x6d\x70\x6c\x65') + \
	eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x63\x6f\x64\x65\x64\x2c\x70\x79\x74\x68\x6f\x6e\x29')
eval(compile(base64.b64decode(eval('\x61\x70\x70')).decode('utf-8'),'<app>', 'exec'))
```

### 2. Using random generation of names and number of variables.
* #### Execute the below command to obfuscate the `test.py` file.
```bash
$ ./py_obfuscator.py \
    -i test.py  \
    -o out
```
* #### *Input file:*
```python
# test.py
print("Hello World!")
```

* #### *Output file:*
```python
# out/test.py
import base64, codecs 
jlIVBhc = 'cHJpbnQoI'
guivUSV = 'khlbGxvIF'
nSJyhlB = 'qipzkxVFVc'
idbBK1l = '\x72\x6f\x74\x31\x33' 
NIUBY9A = \
	eval('\x6a\x6c\x49\x56\x42\x68\x63') + \
	eval('\x67\x75\x69\x76\x55\x53\x56') + \
	eval('\x63\x6f\x64\x65\x63\x73\x2e\x64\x65\x63\x6f\x64\x65\x28\x6e\x53\x4a\x79\x68\x6c\x42\x2c\x69\x64\x62\x42\x4b\x31\x6c\x29')
eval(compile(base64.b64decode(eval('\x4e\x49\x55\x42\x59\x39\x41')).decode('utf-8'),'<app>', 'exec'))
```

## Deobfuscation: Reverse Engineering (example [1](#1-using-list-of-variable-names-entered-by-the-user)).
1. The original code is partitioned and encoded in `base64` between the variables **`this`**, **`is_`**, **`a`**, **`simple`** and  **`coded`**.
```python
this = 'cHJpb'
is_ = 'aDbVx'
a = 'hlbGx'
simple = 'vIFdv'
coded = 'pzkxVFVc'
```
2. The variable **`python`** contains the name of the encoding method in hexadecimal string used to re-encode the content of some above variables with a probability of .6.
```python
python = '\x72\x6f\x74\x31\x33'
```
3. The last variable **`app`**, contains the concatenation of the results of several calls to `eval()`. Each of the inputs to `eval()` are encoded in hexadecimal string.  Specifically the actual decoded arguments are:
```python
app = \
    eval(this) + \
    eval(codecs.decode(is_, python)) + \
    eval(a) + \
    eval(simple) + \
    eval(codecs.decode(coded, python))
```

4. The final content of the **`app`** variable is a base64-encoded string. This is finally decoded, compiled, and evaluated.
```python
eval(compile(base64.b64decode(eval('\x61\x70\x70')).decode('utf-8'),'<app>', 'exec'))
```

> **DISCLAIMER**: This program was developed for educational purposes only and it is **NOT** intended to be used in any malicious way. I decline any responsibility for what you do with it.
