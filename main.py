from tokenizer import Tokenizer
from parser import Parser
import subprocess

code: str = ""

def main():
    with open("file.glwssa") as program:
        code = program.read()

    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    parser = Parser(tokens, tokenizer.token)
    cpp_code, program_name = parser.parse()

    with open("output.cpp", "w") as output_file:
        output_file.write(cpp_code)

    # Compile the generated C++ file
    compile_command = ["g++", "output.cpp", "-o", f"{program_name}.out"]
    try:
        subprocess.run(compile_command, check=True)
        print(f"Compilation successful. Executable created: ./{program_name}.out")
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e}")

if __name__ == "__main__":
    main()