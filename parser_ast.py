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

from log import log

from typing import Optional as _Optional
from typing import Union as _Union
from typing import List as _List
from typing import Tuple as _Tuple

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

# Expressions __________________________________________________________________________________________

@dataclass
class Literal(Expression):
    value: _Union[int, float, str, bool]

@dataclass
class String(Literal):
    value: str

@dataclass
class Number(Literal):
    value: _Union[int, float]

@dataclass
class Boolean(Literal):
    value: bool


@dataclass
class ProgramName(Expression):
    name: str


@dataclass
class Variable(Expression):
    name: str
    var_type: type


@dataclass
class BinaryOperation(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass
class UnaryOperator(Expression):
    operator: str
    operand: Expression

@dataclass
class Parentheses(Expression):
    exrpession: Expression

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
    variable_list: _List[Variable]


@dataclass
class ExpressionStatement(Statement):
    expression: Expression


class TranspilerBackend_cpp:
    def __init__(self):
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

    def translate_tree(self, tree):
        self.tree = tree

        # translating


class ParserAST:
    def __init__(self, tokens, token):
        self.program_tokens = tokens
        self.tokens = token

        self.variable_table: dict[str, type] = {}
        self.program = Program([])
        self.current_token_index = 0
        self.program_name = "a"
        self.code: _List[str] = []


    def current_token(self, index=0) -> _Optional[_Tuple[str, str]]:
        if self.current_token_index < len(self.program_tokens):
            return self.program_tokens[self.current_token_index + index]
        return None  # Return None if out of bounds


    def next_token(self):
        self.current_token_index += 1


    def parse(self):
        self.create_tree()
        self.analyze_types_tree()

        return self.program, self.program_name


    def create_tree(self):
        while self.current_token_index < len(self.program_tokens):
            token = self.current_token()
            if token is None:
                break  # Exit if no more tokens

            token_type, _ = token
            if token_type == 'PROGRAM':
                self.parse_program_name()
            elif token_type == 'VARIABLES':
                self.parse_declaration()
                # print("Parsing variables...")
            elif token_type == 'READ':
                self.parse_read()
            elif token_type == 'WRITE':
                self.parse_write()
            elif token_type == 'ASSIGN':
                self.parse_assignment()
            elif token_type == 'IF':
                self.parse_if()
            elif token_type == 'END_PROGRAM':
                print("End of program reached.")
                self.next_token()  # Advance to the next token
            else:
                self.next_token()  # Skip unhandled tokens

            # Stop parsing if the current token index reaches the last token
            if self.current_token_index >= len(self.program_tokens):
                break


    def parse_expression(self):
        """
        OR: and, OR = Ή
        AND: not, AND = KAI
        NOT: condition, NOT = ΟΧΙ (unary expression)
        CONDITION: expr, > | < | >= | <= | == | !=
        EXPR: term, ADDITION | SUBTRACTION
        TERM: power, MUL | DIV
        POWER: factor, POW = ^
        FACTOR: NUMBER | FLOAT and LPAREN | RPAREN
        """        
        tree = self.parse_logical_or()
        print(tree)
        return tree

    # __________________________________________________________________________________________________

    def expect(self, expected_type) -> None:
        """
        Checks token, and raises an exception if it is not expected.

        Progresses the token.
        """
        if self.current_token()[0] != expected_type:
            raise SyntaxError(f"Expected {expected_type}")
        self.next_token()


    def parse_logical_or(self):
        node = self.parse_logical_and()

        token_type, token_value = self.current_token()
        while token_type == 'OR':
            self.expect('OR')
            node = BinaryOperation(left=node, operator='OR', right=self.parse_logical_and())

            token_type, token_value = self.current_token()

        return node


    def parse_logical_and(self):
        node = self.parse_condition()

        token_type, token_value = self.current_token()
        while token_type == 'AND':
            self.expect('AND')
            node = BinaryOperation(left=node, operator='AND', right=self.parse_condition())

            token_type, token_value = self.current_token()

        return node


    def parse_condition(self):
        """
        Every condition should be here. One condition is not better than any other.
        """
        node = self.parse_expr()

        token_type, token_value = self.current_token()
        while token_type in {'GT', 'LT', 'GTE', 'LTE', 'NEQ', 'EQ'}:
            op = token_type
            self.expect(token_type)
            
            right = self.parse_expr()
            node = BinaryOperation(left=node, operator=op, right=right)

            token_type, token_value = self.current_token()

        return node


    def parse_expr(self) -> _Union[BinaryOperation, Expression]:
        node = self.parse_term()

        token_type, token_value = self.current_token()
        while token_type in {'PLUS', 'MINUS'}:

            op = token_type
            self.expect(token_type)

            right = self.parse_term()
            node = BinaryOperation(left=node, operator=op, right=right)

            token_type, token_value = self.current_token()

        return node


    def parse_term(self) -> _Union[BinaryOperation, Expression]:
        node = self.parse_power()
    
        token_type, token_value = self.current_token()
        while token_type in {'MUL', 'FDIV', 'IDIV', 'MOD'}:
        
            op = token_type
            self.expect(token_type)
    
            right = self.parse_power()
            node = BinaryOperation(left=node, operator=op, right=right)
    
            token_type, token_value = self.current_token()
    
        return node

    
    def parse_power(self) -> _Union[BinaryOperation]:
        node = self.parse_unary()

        token_type, token_value = self.current_token()
        while token_type == 'POW':
            self.expect('POW')
            
            right = self.parse_power()
            node = BinaryOperation(left=node, operator='POW', right=right)
        
            token_type, token_value = self.current_token()

        return node


    def parse_unary(self):
        token_type, token_value = self.current_token()
        while token_type in {'NOT','MINUS'}:
            if token_type == 'NOT':
                self.expect('NOT')
                operand = self.parse_unary()
                return UnaryOperator(operator='NOT', operand=operand) 
            elif token_type == 'MINUS':
                self.expect('MINUS')
                operand = self.parse_unary()
                return UnaryOperator(operator='MINUS', operand=operand) 

        return self.parse_factor()


    def parse_factor(self) -> _Union[Number, Expression]:
        """
        Simple numbers (0-9) INT, FLOAT
        And parenetheses LPAREN and RPAREN
        """
        token_type, token_value = self.current_token()

        if token_type == "NUMBER":
            self.expect("NUMBER")
            return Number(token_value)
        
        elif token_type == "BOOLEAN":
            self.expect("BOOLEAN")
            return Boolean(token_value)

        elif token_type == "IDENTIFIER":
            self.expect("IDENTIFIER")
            
            if not self.variable_table.get(token_value, False):
                raise SyntaxError(f"Variable {token_value} does not exist.")
            return Variable(token_value, self.variable_table[token_value])

        elif token_type == "LPAREN":
            self.expect("LPAREN")
            node = self.parse_expr()
            self.expect("RPAREN")
            return node

        else:
            raise SyntaxError(f"Unexpected token: {token_type}, with value: {token_value}")


    # __________________________________________________________________________________________________


    def parse_program_name(self):
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
        log("From parse_declaration: Succesfully parsed program name ", tags=["vd"])


    def parse_declaration(self):
        """
        There is a section in the code, named VARIABLES, where you put all the variables at.

        This method creates the nodes for that section.
        """
        # skips the tokens that we do not need e.g. ['NEWLINE', 'VARIABLES']
        while self.current_token() and self.current_token()[0] in ['NEWLINE', 'VARIABLES']:
            self.next_token()
        
        log("From parse_declaration: Started Variable ", tags=["vd"])

        VALID_VARIABLE_TYPES = {'INTEGERS', 'CHARACTERS', 'REAL', 'LOGICAL'}

        while self.current_token() and self.current_token()[0] in VALID_VARIABLE_TYPES:
            token_type, _ = self.current_token()

            if token_type == 'INTEGERS':
                for name in self.read_variable_list():
                    log("From parse_declaration: Creating Node for VariableDeclaration with name:", name, "Type: int", tags=["vd"])
                    self.variable_table[name] = int
                    self.program.body.append(VariableDeclaration(name, int))
            elif token_type == 'CHARACTERS':
                for name in self.read_variable_list():
                    log("From parse_declaration: Creating Node for VariableDeclaration with name:", name, "Type: str", tags=["vd"])
                    self.variable_table[name] = str
                    self.program.body.append(VariableDeclaration(name, str))
            elif token_type == 'REAL':
                for name in self.read_variable_list():
                    log("From parse_declaration: Creating Node for VariableDeclaration with name:", name, "Type: float", tags=["vd"])
                    self.variable_table[name] = float
                    self.program.body.append(VariableDeclaration(name, float))
            elif token_type == 'LOGICAL':
                for name in self.read_variable_list():
                    log("From parse_declaration: Creating Node for VariableDeclaration with name:", name, "Type: bool", tags=["vd"])
                    self.variable_table[name] = bool
                    self.program.body.append(VariableDeclaration(name, bool))
            else:
                raise SyntaxError(f"Unexpected variable type '{token_type}'")

            self.next_token()  # Move to the next token after processing the type


    def read_variable_list(self):
        log("From read_variable_list: Parsing the variable list", tags=["vd"])

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
        
        log("From parse_declaration: Found these variables:", variables, tags=["vd"])
        
        return variables
    

    def parse_read(self):
        self.next_token()  # Skip 'ΔΙΑΒΑΣΕ'

        VALID_READ_WRITE_TOKENS = {'IDENTIFIER', 'COMMA'}
        read = Read()
        while self.current_token() and self.current_token()[0] != 'NEWLINE':
            token_type, var_name = self.current_token()
            if token_type not in VALID_READ_WRITE_TOKENS:
                raise SyntaxError(f"Unexpected token '{var_name}' in read command.")
            if token_type == 'IDENTIFIER':
                try:
                    read.variable_list.append(Variable(var_name, self.variable_table[var_name]))
                except KeyError as e:
                    raise SyntaxError(f"Variable {var_name} has not been declared in Variables section. ({e})")

            self.next_token()  # Move to the next token
        
        self.program.body.append(read)


    def parse_write(self):
        VALID_READ_WRITE_TOKENS = VALID_PROCESS_EXPRESSION_TOKENS
        END_TOKENS = {'NEWLINE', 'COMMA'}

        self.next_token()  # Skip 'ΓΡΑΨΕ'
        expr_list: _List[Expression] = []
        
        while self.current_token() and self.current_token()[0] != 'NEWLINE':
            # Process each part of the expression until a comma or newline is encountered
            part_tokens = self.parse_expression()
            expr_list.append(part_tokens)

            # If the current token is a comma, skip it and continue
            if self.current_token() and self.current_token()[0] == 'COMMA':
                self.next_token()


        self.program.body.append(Write(expr_list))


    def parse_assignment(self):
        ...

    
    def parse_statement(self):
        ...


    def analyze_types_tree(self, expected_final_type: str | None = None) -> str | None:
        ...