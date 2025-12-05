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
    return_type: type_______________
    body: Block


@dataclass
class ExpressionStatement(Statement):
    expression: Expression

# Expressions __________________________________________________________________________________________

@dataclass
class Literal(Expression):
    value: _Union[int, float, str, bool]


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


    def create_tree(self) -> str:
        while self.current_token() and self.current_token()[0] not in end_tokens:
            token_type, token_value = self.current_token()

            if token_type not in valid_tokens.union({'LPAREN', 'RPAREN', 'BUILTIN_FUNCTION'}):
                raise SyntaxError(f"Unexpected token type :'{token_type}' and value :'{token_value}' in expression")

            if token_type == "LPAREN":
                self.parse_expression()


    def parse_declaration(self):
        ...


    def parse_assignment(self):
        ...

    
    def parse_statement(self):
        ...

    
    def parse_expression(self):
        ...


    def parse_binary_operation(self):
        ... 


    def parse_unary_operation(self):
        ... 



    def analyze_types_tree(self, expected_final_type: str | None) -> str | None:
        ...


    def parse_tree(self) -> _List:
        ...