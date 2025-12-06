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

VALID_VARIABLE_TYPES = {'INTEGERS', 'CHARACTERS', 'REAL', 'LOGICAL'}
VALID_PROCESS_EXPRESSION_TOKENS = {
    'IDENTIFIER',
    'NUMBER', 'FLOAT', 'STRING', 'LOGICAL', 
    'OP',
    'GT', 'LT', 'GTE', 'LTE', 'NEQ', 'EQ', 
    'NOT', 'AND', 'OR', 'MOD', 'DIV',
    'BUILTIN_FUNCTION', 'LPAREN', 'RPAREN'
}

from dataclasses import dataclass

from typing import Optional as _Optional
from typing import Union as _Union
from typing import List as _List

class Node:
    ...

class Statement(Node):
    """
    A statement is anything that executes a commad. 
    e.g. if, while, for, etc
    """


class Expression(Node):
    """
    An expression is expects to give back a Value
    """

@dataclass
class Program:
    body: list[Statement]


# Statements _______________________________________________________________________________________________

@dataclass
class Block(Statement):
    """
    Are the commands inside the if blocks, while blocks etc
    """
    body: list[Statement]


@dataclass
class VariableDeclaration(Statement):
    """
    When the variable is declared in glwssa it has Public, scope and the type MUST be declared
    """
    name: str
    var_type: type


@dataclass
class VariableAssignement(Statement):
    """
    Because in GLWSSA you declare the variables you use globally, assignement should be different.
    (Type is not preserved here because there is a variable table where it will be type checked) 
    """
    target: str
    expr: Expression


@dataclass
class If(Statement):
    condition: Expression
    then_brach: Block
    else_branch: _Optional[Statement]


@dataclass
class While(Statement):
    condition: Expression
    body: Block


@dataclass
class ProcedureDecl(Statement):
    """
    In GLWSSA you have an additional function type, named procedure. 
    Which doesn't return a variable. But any variables that you pass and change will be changed globally.
    """
    name: str
    params: list[VariableDeclaration]
    body: Block


@dataclass
class FunctionDecl(Statement):
    """
    Normal function like any other language, it takes (a fixed amount) parameters, and it gives back only one 
    value. 
    """
    name: str
    params: list[VariableDeclaration]
    return_type: type
    body: Block


@dataclass
class Write(Statement):
    expression: _List[Expression]


@dataclass
class Read(Statement):
    expression: _List[Expression]


@dataclass
class ExpressionStatement(Statement):
    expression: Expression

# Expressions __________________________________________________________________________________________

@dataclass
class Literal(Expression):
    value: _Union[int, float, str, bool]


@dataclass
class ProgramName(Expression):
    name: str


@dataclass
class Variable(Expression):
    name: str


@dataclass
class BinaryOperation(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryOperator(Expression):
    operator: str
    operand: Expression



class ParserAST:
    def __init__(self, tokens, token):
        self.program_tokens = tokens
        self.tokens = token
        self.program = Program()
        self.current_token_index = 1
        self.program_name = "a"
        self.code: _List[str] = []
        self.greek_to_english = {
            'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E',
            'Ζ': 'Z', 'Η': 'H', 'Θ': 'TH', 'Ι': 'I', 'Κ': 'K',
            'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O',
            'Π': 'P', 'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y',
            'Φ': 'F', 'Χ': 'CH', 'Ψ': 'PS', 'Ω': 'W'
        }
        self.operator_mapping = {
            'NEQ': '!=',  # Not equal
            'EQ': '==',   # Equal
            'GT': '>',    # Greater than
            'LT': '<',    # Less than
            'GTE': '>=',  # Greater than or equal
            'LTE': '<=',  # Less than or equal
            'AND': '&&',  # Logical AND
            'OR': '||',   # Logical OR
            'NOT': '!',   # Logical NOT
            'MOD': '%',   # Modulus operator
            'DIV': '/',   # Division operator
        }




    def current_token(self, index=0):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index + index]
        return None  # Return None if out of bounds


    def next_token(self):
        self.current_token_index += 1


    def parse(self):
        self.create_tree()
        self.analyze_types_tree()
        self.parse_tree()

        return self.code, self.program_name


    def create_tree(self):
        while self.current_token_index < len(self.tokens):
            token = self.current_token()
            if token is None:
                break  # Exit if no more tokens
            token_type, token_value = token
            if token_type == 'PROGRAM':
                self.tree_program_name()
            elif token_type == 'VARIABLES':
                self.tree_declaration()
                # print("Parsing variables...")
            elif token_type == 'READ':
                self.tree_read()
            elif token_type == 'WRITE':
                self.tree_write()
            elif token_type == 'ASSIGN':
                self.tree_assignment()
            elif token_type == 'IF':
                self.parse_if()
            elif token_type == 'END_PROGRAM':
                print("End of program reached.")
                self.cpp_code.append("return 0;\n}")
                self.next_token()  # Advance to the next token
            else:
                self.next_token()  # Skip unhandled tokens

            # Stop parsing if the current token index reaches the last token
            if self.current_token_index >= len(self.tokens):
                break


    def tree_program_name(self):
        """
        Adds the first Node of the program, which should be the name.

        Realistically, if the tokenizer, didn't find a PROGRAM_NAME token, then there 
        would've been already an error. 
        
        But neven be too sure...
        """
        self.next_token()  # Skip 'ΠΡΟΓΡΑΜΜΑ'
        if not self.current_token() or self.current_token()[0] != 'PROGRAM_NAME':
            raise SyntaxError("Expected program name after 'ΠΡΟΓΡΑΜΜΑ'")
        _, self.program_name = self.current_token()
        self.program.body.append(ProgramName(self.program_name)) # purely symbolical


    def tree_declaration(self):
        """
        There is a section in the code, named VARIABLES, where you put all the variables at.

        This method creates the nodes for that section.
        """
        # skips the tokens that we do not need e.g. ['NEWLINE', 'VARIABLES']
        while self.current_token() and self.current_token()[0] in ['NEWLINE', 'VARIABLES']:
            self.next_token()

        VALID_VARIABLE_TYPES = {'INTEGERS', 'CHARACTERS', 'REAL', 'LOGICAL'}

        while self.current_token() and self.current_token()[0] in VALID_VARIABLE_TYPES:
            token_type, _ = self.current_token()

            if token_type == 'INTEGERS':
                for name in range(self.read_variable_list()):
                    self.program.body.append(VariableDeclaration(name, int))
            elif token_type == 'CHARACTERS':
                for name in range(self.read_variable_list()):
                    self.program.body.append(VariableDeclaration(name, str))
            elif token_type == 'REAL':
                for name in range(self.read_variable_list()):
                    self.program.body.append(VariableDeclaration(name, float))
            elif token_type == 'LOGICAL':
                for name in range(self.read_variable_list()):
                    self.program.body.append(VariableDeclaration(name, bool))
            else:
                raise SyntaxError(f"Unexpected variable type '{token_type}'")

            self.next_token()  # Move to the next token after processing the type


    def read_variable_list(self):
        variables = []
        self.next_token()  # Skip the type token (e.g., 'ΑΚΕΡΑΙΕΣ')

        # Ensure the next token is a colon
        if not self.current_token() or self.current_token()[0] != 'COLON':
            raise SyntaxError("Expected ':' after variable type")
        self.next_token()  # Skip the colon

        # read variable names
        while self.current_token() and self.current_token()[0] == 'IDENTIFIER':
            _, var_name = self.current_token()
            variables.append(var_name)
            self.next_token()  # Move to the next token
            if self.current_token() and self.current_token()[0] == 'COMMA':
                self.next_token()  # Skip the comma

        if not variables:
            raise SyntaxError("Expected at least one variable name")
        return variables
    

    def tree_write(self):
        ...


    def tree_read(self):
        ...


    def tree_assignment(self):
        ...

    
    def tree_statement(self):
        ...

    
    def tree_expression(self):
        ...


    def tree_binary_operation(self):
        ... 


    def tree_unary_operation(self):
        ... 


    def analyze_types_tree(self, expected_final_type: str | None) -> str | None:
        ...


    def parse_tree(self) -> _List:
        ...