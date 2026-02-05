from dataclasses import dataclass

from typing import Optional as _Optional
from typing import Union as _Union
from typing import List as _List

from .tokens import Token

class Node:
    ...

class Statement(Node):
    """
    A statement is anything that executes a command. 
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
class Callable:
    name: Token
    params: list[_Union[Expression]]
    body: list[Statement]

@dataclass
class Function(Callable):
    func_type: Expression


@dataclass
class Procedure(Callable): ...


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
    """
    The variable dataclass can store single values variables, arrays and whatever else.

    The type of the variable is stored (obviously) in the var_type attribute.
    
    """
    name: str
    var_type: Expression


@dataclass 
class IntType(Expression): ...


@dataclass
class RealType(Expression): ...


@dataclass
class CharType(Expression): ...


@dataclass
class BoolType(Expression): ...


@dataclass
class ArrayType(Expression):
    """
    val_type can be any of the above types, exception is the ArrayType.

    Theoretically I could make the representation a recurcive Array for multidimensional arrays.
    but the val_dim is a better choice, because it can easily indexed.
    """
    val_dim: _List[Expression]
    val_type: Expression


@dataclass
class StructType(Expression):
    ...


@dataclass
class ArrayIndex(Expression):
    name: str
    index_dim: _List[Expression]
    var_type: str


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
    variable: Variable


@dataclass
class ConstantDeclaration(Statement):
    name: str
    expr: Expression


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
    condition: _Union[Expression, _List[Expression]]
    body: Block


@dataclass
class If(Statement):
    branches: _List[Branch]
    else_branch: _Optional[Statement]


@dataclass
class Switch(Statement):
    expr: Expression
    branches: _List[Branch]
    else_branch: _Optional[Statement]


@dataclass
class While(Statement):
    condition: Expression
    body: Block


@dataclass
class For(Statement):
    counter: Variable
    from_expr: Expression
    to_expr: Expression
    step: _Union[Number, Float] # is this lore accurate?
    body: Block


@dataclass
class Do(Statement):
    condition: Expression
    body: Block


@dataclass
class CallProcedure(Statement):
    name: str
    params: list[Variable]


@dataclass 
class CallFunction(Statement):
    name: str
    params: list[Expression]
    func_type: Expression


@dataclass
class Write(Statement):
    expression: _List[Expression]


@dataclass
class Read(Statement):
    variable_list: _List[Variable]


@dataclass
class ReturnExpression(Statement):
    return_expr: Expression


TYPE_TABLE = {
    "INTEGERS": IntType,
    "CHARACTERS": CharType,
    "REALS": RealType,
    "LOGICALS": BoolType,
}

TYPE_TABLE_FUNC = {
    "INTEGER": IntType,
    "CHARACTER": CharType,
    "REAL": RealType,
    "LOGICAL": BoolType,
}

# __all__ = [
#     "Expression",
#     "Statement",
#     "Program",
#     "Callable"
#     "Function",
#     "Procedure",
#     "Literal", "String", "Number", "Float", "Boolean",
# ]
