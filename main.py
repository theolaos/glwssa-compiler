# MIT License

# Copyright (c) 2025 Theolaos

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import subprocess
import os

from src.tokenizer import Tokenizer
from src.parser import Parser
from src.parser_ast import ParserAST
from src.analyzer import TreeAnalyzer
from src.backend import TranspilerBackend_cpp
from src.log import set_global_tags, log, flush_log_file

def main():
    code: str = ""
    compile_command: list[str] = []
    
    with open("file.glwssa") as program:
        code = program.read()

    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    parser = Parser(tokens, tokenizer.token)
    cpp_code, program_name = parser.parse()

    with open("output.cpp", "w") as output_file:
        output_file.write(cpp_code)

    # Detect the operating system
    is_windows = os.name == "nt"

    # Set the compile command based on the OS
    if is_windows: # https://github.com/niXman/mingw-builds-binaries?tab=readme-ov-file
        compile_command = ["/mingw64/bin/g++.exe", "output.cpp", "-o", f"{program_name}.exe"]
    else:
        compile_command = ["g++", "output.cpp", "-o", f"{program_name}.out"]

    # Compile the generated C++ file
    try:
        subprocess.run(compile_command, check=True)
        executable = f"{program_name}.exe" if is_windows else f"{program_name}.out"
        print(f"Compilation successful. Executable created: ./{executable}")
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e}")


def main_with_ast():
    # v - verbose
    # debug - debugging duh
    # vd - variable declaration
    # tok - tokens
    # atok - logs all the tokens of the loaded program
    # mtok - logs the method tokenize
    # pvb - parse variable block
    # expr - expressions
    # r - from parse read
    # ct - create tree
    flush_log_file()
    set_global_tags(tags=["all"], exclude_tags=["mtok"])

    log("From main func (main.py): main function started.", tags=["v"])

    code: str = ""
    compile_command: list[str] = []
    
    with open("file.glwssa") as program:
        code = program.read()

    log("From main func (main.py): Code has been succesfully read", tags=["v"])

    tokenizer = Tokenizer(code)
    # tokens = tokenizer.tokenize()
    tokens = tokenizer.tokenize_with_lines()
    log("From main func (main.py): Code has been succesfully tokenized", tags=["v"])

    parser = ParserAST(tokens, tokenizer.token)
    log("From main func (main.py): The parser has been succesfully initialized", tags=["v"])
    program_ast, program_name = parser.parse()
    log("From main func (main.py): Code has been succesfully parsed", tags=["v"])
    log("From main func (main.py): The program name is", program_name, tags=["v"])

    analyzer = TreeAnalyzer()
    log("From main func (main.py): Starting analyzing of the tree", tags=["v"])
    analyzer.analyze_types_tree(program_ast)
    log("From main func (main.py): Program tree analyzer is ", tags=["v"])


    backend = TranspilerBackend_cpp()
    log("From main func (main.py): The backend has been succesfully initialized", tags=["v"])
    cpp_code = backend.translate_tree(program_ast)
    log("From main func (main.py): Code has been succesfully parsed", tags=["v"])

    with open("output.cpp", "w") as output_file:
        output_file.write(cpp_code)

    log("From main func (main.py): The cpp code output has been transferred into the output.cpp file", tags=["v"])

    # Detect the operating system
    is_windows = os.name == "nt"

    log("From main func (main.py): Detected OS is:", "Windows" if is_windows else "Linux", tags=["v"])

    # Set the compile command based on the OS
    if is_windows: # https://github.com/niXman/mingw-builds-binaries?tab=readme-ov-file
        compile_command = ["/mingw64/bin/g++.exe", "output.cpp", "-o", f"{program_name}.exe"]
    else:
        compile_command = ["g++", "output.cpp", "-o", f"{program_name}.out"]

    log("From main func (main.py): Running this command:", compile_command, tags=["v"])


    # Compile the generated C++ file
    try:
        subprocess.run(compile_command, check=True)
        executable = f"{program_name}.exe" if is_windows else f"{program_name}.out"
        log("From main func (main.py): The cpp code has been succesfully compiled into an executable, named:", executable, tags=["v"])
        print(f"Compilation successful. Executable created: ./{executable}")
    except subprocess.CalledProcessError as e:
        log("From main func (main.py): Failed to compile because, see error:\n", e, tags=["v"])
        print(f"Compilation failed: {e}")


if __name__ == "__main__":
    # main()
    main_with_ast()