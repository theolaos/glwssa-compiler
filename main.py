# This file is part of: glwssa-compiler 
# Copyright (C) 2025  @theolaos
# glwssa-compiler is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import subprocess
import os

import traceback

from src.error import ErrorStack
from src.tokenizer import Tokenizer
from src.parser_ast import ParserAST
from src.analyzer import TreeAnalyzer
from src.backend import TranspilerBackend_cpp
from src.log import set_global_tags, log, flush_log_file


def main():
    # e - error
    # v - verbose
    # b - if/for block
    # eta - expect_token_alone is a method in ParserAST
    # pi - parse_if method for parsing and creating the AST tree of If
    # debug - debugging duh
    # vd - variable declaration
    # tok - tokens
    # atok - logs all the tokens of the loaded program
    # mtok - logs the method tokenize
    # pvb - parse variable block
    # expr - expressions
    # r - from parse read
    # ct - create tree
    # nodes - prints all the nodes of the AST tree
    # pcp - parse call procedure
    flush_log_file()
    # set_global_tags(tags=["e"])
    set_global_tags(tags=["all"], exclude_tags=["mtok"])

    log("From main func (main.py): main function started.", tags=["v"])

    code: str = ""
    compile_command: list[str] = []
    
    with open("file.glwssa") as program:
        code = program.read()

    log("From main func (main.py): Code has been succesfully read", tags=["v"])

    error_stack = ErrorStack()
    log("From main func (main.py): Initialized successfully the errorstack", tags=["v"])


    tokenizer = Tokenizer(code)
    # tokens = tokenizer.tokenize()
    tokens = tokenizer.tokenize_with_lines()
    log("From main func (main.py): Code has been succesfully tokenized", tags=["v"])

    parser = ParserAST(tokens, tokenizer.token)
    log("From main func (main.py): The parser has been succesfully initialized", tags=["v"])
    program_ast, program_name = parser.parse()
    log("From main func (main.py): Code has been succesfully parsed", tags=["v"])
    log("From main func (main.py): The program name is", program_name, tags=["v"])
    log("From main func (main.py): Printing the Nodes of the AST tree", tags=['v'])
    for node in program_ast.body:
        log(node, tags=['nodes'])

    analyzer = TreeAnalyzer()
    log("From main func (main.py): Starting analyzing of the tree", tags=["v"])
    analyzer.analyze_types_tree(program_ast)
    log("From main func (main.py): Program tree analyzer is ", tags=["v"])


    backend = TranspilerBackend_cpp()
    log("From main func (main.py): The backend has been succesfully initialized", tags=["v"])
    cpp_code = backend.translate_tree(program_ast)
    log("From main func (main.py): Code has been succesfully parsed", tags=["v"])


    if not error_stack.errors:
        error_stack.print_errors()
        return
    
    error_stack.print_warnings()

    error_stack.print_notes()


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
    try:
        main()
    except:
        error_traceback = traceback.format_exc()
        log(error_traceback, ["e"], "both")
        print("ΣΦΑΛΜΑ <I999> : Εσωτερικό σφάλμα του Διαμεταγλωττιστή.")
        print("Τρέξε τον κώδικα σου με tags='all' exclude_tags='mtok' και έπειτα στείλε το '.log' αρχείο μαζί με τον", end="")
        print(" κώδικα σου σε ένα νέο Issue στο github page του glwssa-compiler - https://github.com/theolaos/glwssa-compiler")