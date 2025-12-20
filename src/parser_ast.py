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

TYPE_MAP = {
    'INTEGERS': "int",
    'CHARACTERS': "string",
    'REAL': "float",
    'LOGICAL': "bool",
}

from dataclasses import dataclass

from .log import log

from .tokens import Token

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
    value: int

@dataclass
class Float(Literal):
    value: float

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
class Branch:
    condition: Expression
    body: Block

@dataclass
class If(Statement):
    branches: _List[Branch]
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


class ParserAST:
    def __init__(self, tokens, token):
        self.program_tokens: _List[_List[_Tuple[str, str]]] = tokens
        self.tokens = token

        self.variable_table: dict[str, type] = {}
        self.program = Program([])
        self.program_name = "a"
        self.code: _List[str] = []

        self.current_token_index = 0
        self.current_line = 0


    def current_token(self, index: int =0, default: Token = Token('NO_TOKEN','NO_VALUE', -1, -1)) -> Token:
        """
        Retrieves the current token. It does not raise a Out of Bounds error, it gives you the default instead.
        
        :param index: Get the current_token + index
        :type index: int
        :param default: if there is no current_token, then it return the default token
        :type default: Tuple[str, str]
        :return: Returns the current token
        :rtype: Tuple[str, str]
        """
        if len(self.program_tokens[self.current_line]) == 0:
            return ('EMPTY_LINE', 'NO_VALUE')
        if self.current_token_index + index < len(self.program_tokens[self.current_line]) and self.current_token_index + index >= 0:
            return self.program_tokens[self.current_line][self.current_token_index + index]
        return default  # Return None if out of bounds


    def next_token(self):
        self.current_token_index += 1


    def next_line(self):
        self.current_line += 1
        self.current_token_index = 0


    def parse(self):
        self.create_tree()
        return self.program, self.program_name


    def create_tree(self):
        while self.current_line < len(self.program_tokens):
            token_type = self.current_token().kind

            log(f"From create tree(parser_ast.py): Parsing line {self.current_line}, index {self.current_token_index}. Current token type is {token_type}", tags=['debug', 'ct'])

            if token_type == 'PROGRAM':
                log(f"From create tree(parser_ast.py): Found PROGRAM in line {self.current_line}", tags=['debug', 'ct'])
                self.parse_variables_block()
                self.parse_code_block()                
            elif token_type == 'PROCEDURE':
                log(f"From create tree(parser_ast.py): Found PROCEDURE in line {self.current_line}", tags=['debug', 'ct'])
                self.parse_procedure()
            elif token_type == 'FUNCTION':
                log(f"From create tree(parser_ast.py): Found FUNCTION in line {self.current_line}", tags=['debug', 'ct'])
                self.parse_function()
            elif token_type == 'EMPTY_LINE':
                log(f"From create tree(parser_ast.py): Found an empty line {self.current_line}, skipping it", tags=['debug', 'ct'])
                self.next_line()
                continue
            
            if self.current_line >= len(self.program_tokens):
                log("From create tree(parser_ast.py): Finished creating tree", tags=['ct'])
                break


    def parse_variables_block(self):
        self.expect_tokens_line(2)
        self.next_token()
        self.parse_program_name(self.program)
        log(f'From parse_variables_block (parser_ast.py): Got programs name {self.program_name}', tags=['pvb'])
        self.next_line()
        self.expect_token_alone('VARIABLES')
        self.next_line()

        self.parse_declaration(self.program)
        log(f'From parse_variables_block (parser_ast.py): Finished parsing the variables', tags=['pvb'])
        
        self.expect_token_alone('START')
        self.next_line()


    def parse_code_block(self):
        while self.current_line < len(self.program_tokens):
            token_type = self.current_token().kind
            if token_type == 'READ':
                log(f"From parse_code_block (parser_ast.py): Found READ in main program.", tags=["v"])
                self.parse_read(self.program)
                self.next_line()
            elif token_type == 'WRITE':
                log(f"From parse_code_block (parser_ast.py): Found WRITE in main program", tags=["v"])
                self.parse_write(self.program)
                self.next_line()
            elif token_type == 'IDENTIFIER':
                log(f"From parse_code_block (parser_ast.py): Found IDENTIFIER/ASSIGNEMENT in main program", tags=["v"])
                self.parse_assignment(self.program)
                self.next_line()
            elif token_type == 'IF':
                log(f"From parse_code_block (parser_ast.py): Found IF in main program", tags=["v"])
                self.parse_if(self.program)
                self.next_line()
            elif token_type == 'END_PROGRAM':
                log(f"From parse_code_block (parser_ast.py): End of program {self.program_name} reached.", tags=["v"])
                self.expect_token_alone('END_PROGRAM')
                self.next_line()
            elif token_type == 'EMPTY_LINE': # theoretically it also works in empty lines
                self.next_line()
            
            # Stop parsing if the current token index reaches the last token
            if self.current_token_index >= len(self.program_tokens):
                break


    def parse_block(self, branch: _Union[Block, Program], end_tokens: _List[str], inner: bool = False) -> _Union[Block, Program]:
        """
        Parse block for and If (ΑΝ), for (ΓΙΑ) blocks
        
        :param self: Description
        :param end_tokens: Description
        """

        log(f"From parse_block (parser_ast.py): {self.current_token()}.", tags=["b"])
        while self.current_token().kind not in end_tokens:
            log(f"From parse_block (parser_ast.py): {self.current_token()}.", tags=["b"])
            token = self.current_token()
            token_type = token.kind
            if token_type == 'WRITE':
                log(f"From parse_block (parser_ast.py): Inside IF/FOR found WRITE", tags=["b"])
                self.parse_write(branch)
                self.next_line()
            elif token_type == 'READ':
                log(f"From parse_block (parser_ast.py): Inside IF/FOR found READ", tags=["b"])
                self.parse_read(branch)
                self.next_line()
            elif token_type == 'IF': 
                log(f"From parse_block (parser_ast.py): Inside IF/FOR found IF", tags=["b"])
                self.parse_if(branch)  # Handle nested if statements
                self.next_line()
            elif token_type == 'IDENTIFIER':
                log(f"From parse_block (parser_ast.py): Inside IF/FOR found ASSIGN", tags=["b"])
                self.parse_assignment(branch)
                self.next_line()
            elif token_type in end_tokens:
                break
        log("From parse_block (parser_ast.py): Finished IF/FOR block.", tags=["b"])


    def parse_expression(self):
        """
        OR: and, OR = Ή
        AND: not, AND = KAI
        NOT: condition, NOT = ΟΧΙ (unary expression)
        CONDITION: expr, > | < | >= | <= | == | !=
        EXPR: term, ADDITION | SUBTRACTION
        TERM: power, MUL | DIV
        POWER: factor, POW = ^
        FACTOR: NUMBER | FLOAT and LPAREN | RPAREN and VARIABLE = IDENTIFIER = ΜΕΤΑΒΛΗΤΗ
        """        
        tree = self.parse_logical_or()
        log(tree, tags=['expr'])
        return tree

    # __________________________________________________________________________________________________

    def expect_tokens_line(self, n: int) -> None:
        if len(self.program_tokens[self.current_line]) is not n:
            raise SyntaxError(
                f"Expected only {n} tokens in line: {self.current_token(-1).line}. Instead found {len(self.program_tokens[self.current_line])} tokens."
            )   


    def expect_token_alone(self, expected_type: str) -> None:
        """
        Checks if the token is alone in the the line. IT DOES NOT GO TO THE NEXT LINE.
        """
        log(f"From expect_token_alone (parser_ast.py): Expecting token {expected_type}", tags=['eta'])
        self.expect_tokens_line(1)
        self.match(expected_type)
        log(f"From expect_token_alone (parser_ast.py): Found {expected_type}", tags=['eta'])


    def soft_match(self, expected_type) -> bool:
        """
        Checks token, and returns false if the token is not what was expected.
        """
        if self.current_token().kind != expected_type:
            return False
        return True   

    
    def match(self, expected_type: str) -> None:
        """
        Checks token, and raises an exception if it not expected.
        """
        if self.current_token().kind != expected_type:
            raise SyntaxError(f"Expected {expected_type}, but found {self.current_token().kind}, in line {self.current_token().line}")       


    def expect(self, expected_type: str) -> None:
        """
        Checks token, and raises an exception if it is not expected.

        Progresses the token.
        """
        self.match(expected_type=expected_type)
        self.next_token()


    def reached_eol(self) -> bool:
        return self.current_token_index > len(self.program_tokens[self.current_line])-1


    def expect_eol(self) -> None:
        """
        Expects it to be EOL (End of line), if it is not, it throws an error.
        """
        if not self.current_token_index > len(self.program_tokens[self.current_line])-1:
            raise SyntaxError(f"Expected NEWLINE in the end of line: {self.current_line}. Encountered {self.current_token()} instead")


    def parse_logical_or(self):
        node = self.parse_logical_and()
        
        token = self.current_token()
        token_type, token_value = token.kind, token.value

        while token_type == 'OR':
            self.expect('OR')
            node = BinaryOperation(left=node, operator='OR', right=self.parse_logical_and())

            token_type, token_value = self.current_token()

        return node


    def parse_logical_and(self):
        node = self.parse_condition()

        token = self.current_token()
        token_type, token_value = token.kind, token.value

        while token_type == 'AND':
            self.expect('AND')
            node = BinaryOperation(left=node, operator='AND', right=self.parse_condition())

            token = self.current_token()
            token_type, token_value = token.kind, token.value

        return node


    def parse_condition(self):
        """
        Every condition should be here. One condition is not better than any other.
        """
        node = self.parse_expr()

        token = self.current_token()
        token_type, token_value = token.kind, token.value

        while token_type in {'GT', 'LT', 'GTE', 'LTE', 'NEQ', 'EQ'}:
            op = token_type
            self.expect(token_type)
            
            right = self.parse_expr()
            node = BinaryOperation(left=node, operator=op, right=right)

            token = self.current_token()
            token_type, token_value = token.kind, token.value

        return node


    def parse_expr(self) -> _Union[BinaryOperation, Expression]:
        node = self.parse_term()
        
        token = self.current_token()
        token_type, token_value = token.kind, token.value

        while token_type in {'PLUS', 'MINUS'}:

            op = token_type
            self.expect(token_type)

            right = self.parse_term()
            node = BinaryOperation(left=node, operator=op, right=right)

            token = self.current_token()
            token_type, token_value = token.kind, token.value

        return node


    def parse_term(self) -> _Union[BinaryOperation, Expression]:
        node = self.parse_power()

        token = self.current_token()
        token_type, token_value = token.kind, token.value

        while token_type in {'MUL', 'FDIV', 'IDIV', 'MOD'}:
        
            op = token_type
            self.expect(token_type)
    
            right = self.parse_power()
            node = BinaryOperation(left=node, operator=op, right=right)
    
            token = self.current_token()
            token_type, token_value = token.kind, token.value
    
        return node

    
    def parse_power(self) -> _Union[BinaryOperation]:
        node = self.parse_unary()

        token = self.current_token()
        token_type, token_value = token.kind, token.value
        while token_type == 'POW':
            self.expect('POW')
            
            right = self.parse_power()
            node = BinaryOperation(left=node, operator='POW', right=right)
        
            token = self.current_token()
            token_type, token_value = token.kind, token.value
        
        return node


    def parse_unary(self):
        token = self.current_token()
        token_type, token_value = token.kind, token.value
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
        token = self.current_token()
        token_type, token_value = token.kind, token.value

        if token_type == "NUMBER":
            self.expect("NUMBER")
            return Number(token_value)
        elif token_type == "FLOAT":
            self.expect("FLOAT")
            return Float(token_value)
        
        elif token_type == "BOOLEAN":
            self.expect("BOOLEAN")
            return Boolean(token_value)

        elif token_type == "IDENTIFIER":
            self.expect("IDENTIFIER")
            if not self.variable_table.get(token_value, False):
                raise SyntaxError(f"Variable {token_value} does not exist, index {self.current_token_index}, line {self.current_token(-self.current_token_index).line}")
            return Variable(token_value, self.variable_table[token_value])
        elif token_type == "STRING":
            self.expect("STRING")
            return String(token_value)

        elif token_type == "LPAREN":
            self.expect("LPAREN")
            node = self.parse_expr()
            self.expect("RPAREN")
            return node

        else:
            raise SyntaxError(
                f"Unexpected token: {token_type}, with value: {token_value}, index {self.current_token_index}, line {self.current_token(-self.current_token_index).line}"
                )


    # __________________________________________________________________________________________________


    def parse_program_name(self, branch: _Union[Block, Program]):
        """
        Adds the first Node of the program, which should be the name.
        """        
        self.match('PROGRAM_NAME')
        self.program_name = self.current_token().value

        branch.body.append(ProgramName(self.program_name)) # purely symbolical
        log("From parse_declaration (parser_ast.py): Succesfully parsed program name ", tags=["vd"])
        self.next_token()
        self.expect_eol()


    def parse_declaration(self, branch: _Union[Block, Program]): # ΜΕΤΑΒΛΗΤΕΣ section
        """
        There is a section in the code, named VARIABLES, where you put all the variables at.

        This method creates the nodes for that section.
        """
        # parser starts after VARIABLE line
        
        log("From parse_declaration (parser_ast.py): Started Variable ", tags=["vd"])

        while self.current_token().kind in TYPE_MAP:
            token_type = self.current_token().kind

            py_type = TYPE_MAP[token_type]
            self.next_token() # skip type token

            names = self.read_variable_list()
            log("From parse_declaration (parser_ast.py): Creating Node for VariableDeclaration with name:", names, f"Type: {TYPE_MAP[token_type]}", tags=["vd"])
            
            for name in names:
                self.variable_table[name] = py_type
                branch.body.append(VariableDeclaration(name, py_type))

            self.expect_eol()
            self.next_line()


    def read_variable_list(self):
        log("From read_variable_list (parser_ast.py): Parsing the variable list", tags=["vd"])

        variables = []
        # Ensure the next token is a colon
        if not self.current_token() or self.current_token().kind != 'COLON':
            raise SyntaxError("Expected ':' after variable type")
        self.next_token()  # Skip the colon

        # read variable names
        while self.current_token():
            
            self.match('IDENTIFIER')
            
            var_name = self.current_token().value
            variables.append(var_name)
            
            self.next_token()

            if self.soft_match('COMMA'):
                self.next_token()
                continue

            if self.reached_eol():
                break
            
            raise SyntaxError(f"Expected COMMA or NEWLINE, but found {self.current_token()[0]}, {self.current_token(-1)[0]}")

        if not variables:
            raise SyntaxError("Expected at least one variable name")

        log("From read_variable_list (parser_ast.py): Found these variables:", variables, tags=["vd"])
        
        return variables
    

    def parse_read(self, branch: _Union[Block, Program]):
        self.expect('READ')  # Skip 'ΔΙΑΒΑΣΕ'

        read = Read([])
        
        while self.current_token():
            
            self.match('IDENTIFIER')
            token = self.current_token()
            var_name = token.value
            try:
                read.variable_list.append(Variable(var_name, self.variable_table[var_name]))
            except KeyError as e:
                raise SyntaxError(f"Variable {var_name} has not been declared in Variables section. ({e})")
            self.next_token()

            if self.soft_match('COMMA'):
                self.next_token()
                continue

            if self.reached_eol():
                break
            
            raise SyntaxError(f"Expected COMMA or NEWLINE, but found {self.current_token()[0]}")
        
        self.expect_eol()
        log(f"From parse_read (parser_ast.py): Finished parsing the Read (ΔΙΑΒΑΣΕ) in line {self.current_token().line - 1}", tags=["r"])
        branch.body.append(read)


    def parse_write(self, branch: _Union[Block, Program]):
        self.next_token()  # Skip 'ΓΡΑΨΕ'
        expr_list: _List[Expression] = []
        
        while self.current_token():
            # Process each part of the expression until a comma or newline is encountered
            part_tokens = self.parse_expression()
            expr_list.append(part_tokens)

            # If the current token is a comma, skip it and continue
            if self.soft_match('COMMA'):
                self.next_token()
                continue

            if self.reached_eol():
                break

        self.expect_eol()
        branch.body.append(Write(expr_list))


    def parse_assignment(self, branch: _Union[Block, Program]):
        # VALID_ASSIGNMENT_TOKENS = VALID_PROCESS_EXPRESSION_TOKENS
        # END_TOKENS = {'NEWLINE'}

        # Get the variable being assigned to
        token = self.current_token()  # The variable is the token before '<--'
        var_name = token.value
        self.next_token()  # Skip variable
        if not self.variable_table.get(var_name, []):
            raise SyntaxError(f"Variable {var_name} does not exist.")

        self.expect('ASSIGN')

        expression = self.parse_expression()

        # Generate the C++ assignment statement
        if not expression:
            raise SyntaxError(f"Missing expression on the right-hand side of assignment for '{var_name}'")
        
        self.expect_eol()

        node = VariableAssignement(target=var_name, expr=expression)
        branch.body.append(node)


    def parse_if(self, branch: _Union[Block, Program]):
        # creating the branches part of the node. Because there might be a lot of branching
        branches_node = []

        start_line = self.current_token().line
        self.next_token()  # Skip 'ΑΝ' or 'ΑΛΛΙΩΣ_ΑΝ'
        condition_tokens = self.parse_expression()

        self.expect('THEN')
        self.expect_eol()
        self.next_line()

        then_branch = Block([])

        # Parse the body of the IF block
        self.parse_block(then_branch, ['ELSE', 'ELSE_IF','END_IF','END_PROGRAM'])

        branches_node.append(Branch(condition_tokens, then_branch))

        # Handle ΑΛΛΙΩΣ_ΑΝ (else if) recursively
        while self.soft_match('ELSE_IF'):
            log(f"From parse_if (parser_ast.py): Current token in the loop is {self.current_token()}", tags=['pi'])
            # self.next_token() # parse if already skips the IF token (as well the ELSE_IF token)
            self.next_token()
            elif_condition_tokens = self.parse_expression()

            self.expect('THEN')
            self.expect_eol()
            self.next_line()
            temp_elif_branch = Block([])
            self.parse_block(temp_elif_branch, ['ELSE', 'ELSE_IF','END_IF','END_PROGRAM'], True)  # Recursively parse the else-if block
            branches_node.append(Branch(elif_condition_tokens, temp_elif_branch))

        if not branches_node:
            raise SyntaxError(
                f"There are no branches in your if statement, in line {start_line}. Not even a condition, at least type one condition."
            )

        # Handle ΑΛΛΙΩΣ (else)
        else_branch = Block([])
        if self.soft_match('ELSE'):
            self.expect_token_alone('ELSE')
            self.next_line()
            self.parse_block(else_branch, ['END_IF','END_PROGRAM'])
        
        # self.expect_token_alone('END_IF')

        log(f"From parse_if (parser_ast.py): Expecting token {'END_IF'}", tags=['eta'])
        self.expect_tokens_line(1)
        if not self.soft_match('END_IF'):
            raise SyntaxError(
                f"Expected END_IF for the IF scope from line {start_line} but found {self.current_token().kind} instead."
            )
        log(f"From parse_if (parser_ast.py): Found {'END_IF'}", tags=['eta'])

        branch.body.append(
            If(
                branches=branches_node,
                else_branch=else_branch
            )
        )
