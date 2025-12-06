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

from tokenizer import Tokenizer
from parser import Parser
from ast import ParserAST


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
    code: str = ""
    compile_command: list[str] = []
    
    with open("file.glwssa") as program:
        code = program.read()

    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    parser = ParserAST(tokens, tokenizer.token)
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


if __name__ == "__main__":
    # main()
    main_with_ast()