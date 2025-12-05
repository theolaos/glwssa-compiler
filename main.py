import subprocess
import os

from tokenizer import Tokenizer
from parser import Parser


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