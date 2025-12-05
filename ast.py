from dataclasses import dataclass

from typing import Optional as _Optional
from typing import Union as _Union

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
            return self.tokens[self.current_token_index+index]
        return None  # Return None if out of bounds


    def next_token(self):
        self.current_token_index += 1


    def parse(self):
        create_tree()


    def create_tree(self) -> str:
        self.program.body.append()


    def analyze_types_tree(self, expected_final_type: str | None) -> str | None:
        ...