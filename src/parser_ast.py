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

VALID_VARIABLE_TYPES = {"INTEGERS", "CHARACTERS", "REAL", "LOGICAL"}
VALID_PROCESS_EXPRESSION_TOKENS = {
    "IDENTIFIER",
    "NUMBER", "FLOAT", "STRING", "LOGICAL", 
    "OP",
    "GT", "LT", "GTE", "LTE", "NEQ", "EQ", 
    "NOT", "AND", "OR", "MOD", "DIV",
    "BUILTIN_FUNCTION", "LPAREN", "RPAREN"
}

# the tokens below work as brakes, in case the programmer forgot to close the block
END_TOKENS_FOR_BLOCK = ["END_PROGRAM", "FUNCTION", "END_FUNCTION", "PROCEDURE", "END_PROCEDURE"]

from .log import log

from .tokens import Token

from typing import Optional as _Optional
from typing import Union as _Union
from typing import List as _List
from typing import Tuple as _Tuple
from typing import Callable as _Callable


from .ast import *


class ParserAST:
    def __init__(self, tokens, token):
        self.program_tokens: _List[_List[_Tuple[str, str]]] = tokens
        self.tokens = token

        self.program = Program([])

        self.procedures: _List[Callable] = []
        self.functions: _List[Callable] = []

        self.program_name = "a"
        self.code: _List[str] = []

        self.current_token_index = 0
        self.current_line = 0

        self.in_switch = False

        self.parse_block_dict = {
            "WRITE": self.parse_write,
            "READ" : self.parse_read,
            "IDENTIFIER" : self.parse_assignment,
            "IF" : self.parse_if,
            "SWITCH" : self.parse_switch,
            "WHILE" : self.parse_while,
            "FOR" : self.parse_for,
            "START_LOOP" : self.parse_do,
            "CALL" : self.parse_call_procedure,
            # "UNTIL" : self.error_until
        }


        self.parse_program_block_dict = self.parse_block_dict.copy()
        self.parse_program_block_dict.update(
            {
                "END_PROGRAM" : self.parse_end_program
            }
        )
        self.end_program = False


    def current_token(self, index: int=0, default: Token = Token("NO_TOKEN","NO_VALUE", -1, -1, -1, -1)) -> Token:
        """
        Retrieves the current token. It does not raise a Out of Bounds error, it gives you the default instead.
        
        :param index: Get the current_token + index
        :type index: int
        :param default: if there is no current_token, then it return the default token
        :type default: Tuple[str, str]
        :return: Returns the current token
        :rtype: Tuple[str, str]
        """
        if self.current_line >= len(self.program_tokens):
            return default

        if self.current_token_index + index < len(self.program_tokens[self.current_line]) and self.current_token_index + index >= 0:
            return self.program_tokens[self.current_line][self.current_token_index + index]

        if len(self.program_tokens[self.current_line]) == 0:
            return Token("EMPTY_LINE", "NO_VALUE", 0, self.current_line, 0, 0)

        return default  # Return None if out of bounds


    def get_current_line(self) -> int:
        """
        get_current_line, gets the current line that is being parsed
        
        :return: The current line that is being parsed
        :rtype: int
        """
        return self.current_token(-self.current_token_index).line


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

            log(f"From create tree(parser_ast.py): Parsing line {self.current_line}, index {self.current_token_index}. Current token type is {token_type}", tags=["debug", "ct"])

            if token_type == "PROGRAM":
                log(f"From create tree(parser_ast.py): Found PROGRAM in line {self.current_line}", tags=["debug", "ct"])
                self.parse_program_name(self.program)
                self.parse_variables_block(self.program)
                self.parse_program_block(self.parse_program_block_dict)                
            elif token_type == "PROCEDURE":
                log(f"From create tree(parser_ast.py): Found PROCEDURE in line {self.current_line}", tags=["debug", "ct"])
                procedure: Procedure = self.parse_procedure()
                self.procedures.append(procedure)
            elif token_type == "FUNCTION":
                log(f"From create tree(parser_ast.py): Found FUNCTION in line {self.current_line}", tags=["debug", "ct"])
                function: Function = self.parse_function()
                self.functions.append(function)
            elif token_type == "EMPTY_LINE":
                log(f"From create tree(parser_ast.py): Found an empty line {self.current_line}, skipping it", tags=["debug", "ct"])
                self.next_line()
                continue
            
            if self.current_line >= len(self.program_tokens):
                log("From create tree(parser_ast.py): Finished creating tree", tags=["ct"])
                break
    

    def parse_variables_block(self, branch: _Union[Block, Program]) -> None:
        self.next_line()
        if self.soft_match("CONSTANTS"):
            self.expect_token_alone("CONSTANTS")
            self.next_line()
            self.parse_constant_declaration(branch)
            self.next_line()
        

        self.expect_token_alone("VARIABLES")
        self.next_line()

        self.parse_declaration(branch)
        log(f"From parse_variables_block (parser_ast.py): Finished parsing the variables", tags=["pvb"])
        
        self.expect_token_alone("START")
        self.next_line()


    def parse_program_block(self, 
            dict_of_acceptable_tokens: dict[str, _Callable[[_Union[Block, Program]], None]]
        ) -> None:
        while self.current_line < len(self.program_tokens):
            token_type = self.current_token().kind
            if token_type in dict_of_acceptable_tokens:
                log(f"From parse_code_block (parser_ast.py): Found {token_type} in main program. In line {self.get_current_line()}", tags=["v"])
                dict_of_acceptable_tokens[token_type](self.program)
                self.next_line()

            if self.end_program:
                break
        
        if not self.end_program:
            raise SyntaxError("Program did not finish. Don't forget to put END_PROGRAM")


    def parse_block(self, 
            branch: _Union[Block, Program], 
            end_tokens: _List[str], 
            recognizable_tokens: dict[str, _Callable[[_Union[Block, Program]], None]], # {"",func()}
            block_kind: str = "scope"
        ) -> None:
        """
        Parse block for and If (ΑΝ), for (ΓΙΑ) blocks  
        """
        # TODO, should be able to pass the tokens that it can recognize

        log("From parse_block (parser_ast.py): Started parse block.", tags=["b"])
        log(f"From parse_block (parser_ast.py): {self.current_token()} in line {self.get_current_line()}.", tags=["b"])
        while self.current_line < len(self.program_tokens):
            log(f"From parse_block (parser_ast.py): {self.current_token()}.", tags=["b"])
            token = self.current_token()
            token_type = token.kind

            if token_type in recognizable_tokens:
                log(f"From parse_block (parser_ast.py): Inside IF/LOOP found {token_type}", tags=["b"])
                recognizable_tokens[token_type](branch)
                self.next_line()

            if token_type in end_tokens:
                break
        
        if self.current_token().kind not in end_tokens:
            raise SyntaxError(f"{block_kind} did not finish. Don't forget to put the END token of the scope")            


        log("From parse_block (parser_ast.py): Finished parse block.", tags=["b"])

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
        log(f"From expect_token_alone (parser_ast.py): Expecting token {expected_type}", tags=["eta"])
        self.expect_tokens_line(1)
        self.match(expected_type)
        log(f"From expect_token_alone (parser_ast.py): Found {expected_type}", tags=["eta"])


    def soft_match(self, expected_type: str, index: int = 0) -> bool:
        """
        Checks token, and returns false if the token is not what was expected.
        """
        return not self.current_token(index).kind != expected_type

    
    def match(self, expected_type: str) -> None:
        """
        Checks token, and raises an exception if it not expected.
        """
        if self.current_token().kind != expected_type:
            raise SyntaxError(f"Expected {expected_type}, but found {self.current_token().kind}, in line {self.get_current_line()}")       


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
        Expects it to be EOL (End of line), if it is not, it throws an error. It does not go to the next line
        """
        if not self.current_token_index > len(self.program_tokens[self.current_line])-1:
            raise SyntaxError(f"Expected NEWLINE in the end of line: {self.get_current_line()}. Encountered {self.current_token()} instead")


    def reached_eof(self) -> bool:
        """
        In case we reached the end of the file.
        """
        return self.current_line > len(self.program_tokens)-1

    # __________________________________________________________________________________________________

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
        log(tree, tags=["expr"])
        return tree

    # __________________________________________________________________________________________________


    def parse_logical_or(self):
        node = self.parse_logical_and()
        
        token = self.current_token()
        token_type, token_value = token.kind, token.value

        while token_type == "OR":
            self.expect("OR")
            node = BinaryOperation(left=node, operator="OR", right=self.parse_logical_and())

            token_type, token_value = self.current_token()

        return node


    def parse_logical_and(self):
        node = self.parse_condition()

        token = self.current_token()
        token_type, token_value = token.kind, token.value

        while token_type == "AND":
            self.expect("AND")
            node = BinaryOperation(left=node, operator="AND", right=self.parse_condition())

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

        while token_type in {"GT", "LT", "GTE", "LTE", "NEQ", "EQ"}:
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

        while token_type in {"PLUS", "MINUS"}:

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

        while token_type in {"MUL", "FDIV", "IDIV", "MOD"}:
        
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
        while token_type == "POW":
            self.expect("POW")
            
            right = self.parse_power()
            node = BinaryOperation(left=node, operator="POW", right=right)
        
            token = self.current_token()
            token_type, token_value = token.kind, token.value
        
        return node


    def parse_unary(self):
        token = self.current_token()
        token_type, token_value = token.kind, token.value
        while token_type in {"NOT","MINUS"}:
            if token_type == "NOT":
                self.expect("NOT")
                operand = self.parse_unary()
                return UnaryOperator(operator="NOT", operand=operand) 
            elif token_type == "MINUS":
                self.expect("MINUS")
                operand = self.parse_unary()
                return UnaryOperator(operator="MINUS", operand=operand) 

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
        
        elif token_type == "BOOLEAN" and not self.in_switch:
            self.expect("BOOLEAN")
            return Boolean(token_value)

        elif token_type == "IDENTIFIER":
            self.expect("IDENTIFIER")
 
            if self.soft_match("LBRACKET") or self.soft_match("LPAREN"):
                token = self.current_token().kind
                args: _List[Expression] = []
                self.expect(token)
                
                while True:
                    expr = self.parse_expression()
                    args.append(expr)

                    if self.soft_match("COMMA"):
                        self.next_token()
                        continue

                    if self.soft_match(f"R{token[1:]}"): # apperantly brackets are [start:end:step] (?)
                        break

                    raise SyntaxError(f"Expected COMMA or R{token[1:]}, but found {self.current_token().kind} in line {self.get_current_line()}")
                
                self.next_token() # TODO I feel like this will bite me in the ass
                return ArrayIndex(token_value, args, None) if token == "LBRACKET" else CallFunction(token_value, args, None)

            else:
                return Variable(token_value, None)
            
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

    def parse_case_expression(self):
        """
        CONDITION: expr, > | < | >= | <=
        PERIOD: Expr, ..
        ~EXPR: term, ADDITION | SUBTRACTION
        ~TERM: power, MUL | DIV
        ~POWER: factor, POW = ^
        ~FACTOR: NUMBER | FLOAT and LPAREN | RPAREN and VARIABLE = IDENTIFIER = ΜΕΤΑΒΛΗΤΗ

        ~ : These methods are already implemented
        """        
        tree = self.parse_switch_condition()
        log(tree, tags=["expr"])
        return tree
    

    def parse_switch_condition(self):
        token = self.current_token()
        token_type = token.kind
        
        if token_type in {"GT", "LT", "GTE", "LTE"}:
            self.next_token()
            node = self.parse_expr()
            if not (self.reached_eol() or self.current_token().kind == "COMMA"):
                raise SyntaxError(f"Expected Comma or EOL in line: {self.get_current_line()}, instead found {self.current_token()}")
            return UnaryOperator(token_type, node)
        
        return self.parse_period()


    def parse_period(self):
        node = self.parse_expr()

        token = self.current_token()
        token_type = token.kind

        if token_type == "PERIOD": # there cannot be multiple periods
            self.expect("PERIOD")
            self.in_switch = True
            right = self.parse_expr()
            self.in_switch = False
            node = BinaryOperation(node, token_type, right)

        return node

    # __________________________________________________________________________________________________

    def parse_program_name(self, branch: _Union[Block, Program]):
        """
        Adds the first Node of the program, which should be the name.
        """        
        self.expect_tokens_line(2)
        self.next_token()
        self.match("PROGRAM_NAME")
        self.program_name = self.current_token().value

        branch.body.append(ProgramName(self.program_name)) # purely symbolical
        log("From parse_declaration (parser_ast.py): Succesfully parsed program name ", tags=["vd"])
        self.next_token()
        self.expect_eol()


    def parse_end_program(self, branch: _Union[Block, Program]):
        self.match("END_PROGRAM")
        self.end_program = True

        if len(self.program_tokens[self.current_line]) == 2:
            self.next_token()
            self.match("IDENTIFIER")
            if not self.current_token().value == self.program_name:
                raise SyntaxError(f"Expected the progran name in END_PROGRAM to be {self.program_name}, but found {self.current_token().value}. Line: {self.get_current_line()}")
        else:
            self.expect_token_alone("END_PROGRAM")


    def parse_constant_declaration(self, branch: _Union[Block, Program]):
        log("From parse_constant_declaration (parser_ast.py): Started parsing constants ", tags=["vd"])

        while self.soft_match("IDENTIFIER"):
            

            self.match("IDENTIFIER")
            constant_name = self.current_token().value
            self.next_token()
            self.expect("EQ")
            expr = self.parse_expression()
            
            self.expect_eol()

            # self.constants_table[]
            branch.body.append(
                ConstantDeclaration(
                    constant_name, 
                    expr
                )
            )


    def parse_declaration(self, branch: _Union[Block, Program]): # ΜΕΤΑΒΛΗΤΕΣ section
        """
        There is a section in the code, named VARIABLES, where you put all the variables at.

        This method creates the nodes for that section.
        """
        # parser starts after VARIABLE line
        
        log("From parse_declaration (parser_ast.py): Started parsing Variable declaration", tags=["vd"])

        while self.current_token().kind in TYPE_TABLE:
            token_type = self.current_token().kind

            py_type = TYPE_TABLE[token_type]
            self.next_token() # skip type token

            variables: _List[Variable] = self._read_variable_list(py_type)
            log("From parse_declaration (parser_ast.py): Creating Node with list of variables:", variables, f"Type: {TYPE_TABLE[token_type]}", tags=["vd"])
            
            for var in variables:

                branch.body.append(VariableDeclaration(var))
                log("From parse_declaration (parser_ast.py): Created node", 
                    "VariableDeclaration", "with name:", var, f"Type: {var.var_type}", 
                    tags=["vd"]
                )

            self.expect_eol()
            self.next_line()


    def _read_variable_list(self, var_type: str) -> _List[Variable]:
        """
        Docstring for read_variable_list
        
        :param type: Should be a type of this kind INTEGERS, REAL, CHARACTERS, LOGIC 
        :type type: str in INTEGERS, REAL, CHARACTERS, LOGIC
        :return: Returns either a List of variables with arrays
        :rtype: List[Variable]
        """
        
        log("From read_variable_list (parser_ast.py): Parsing the variable list", tags=["vd"])

        # Ensure the next token is a colon
        if not self.current_token() or self.current_token().kind != "COLON":
            raise SyntaxError("Expected ':' after variable type")
        self.next_token()  # Skip the colon

        variables = []
        variables = self._identifier_list(var_type=var_type)

        log("From read_variable_list (parser_ast.py): Found these variables:", variables, tags=["vd"])
        
        return variables
    

    def _identifier_list(self, 
            var_type: _Optional[str] = None, 
            at_least_one_var: bool = True, 
            array_allowed: bool = True,
            inside_paren: bool = False
        ) -> _List[Variable]:
        """
        Creates a list of only IDENTIFIERS, not expressions.
        """
        expr_list = []
        empty: bool = False

        if self.reached_eol() or (self.soft_match("RPAREN") and inside_paren):
            empty = True
        
        if empty and at_least_one_var:
            raise SyntaxError("Expected at least one variable name")

        if empty:
            return expr_list

        while True:
            self.match("IDENTIFIER")
            token = self.current_token()
            var_name = token.value
            array = False

            dim: _List[Expression] = []
            if self.soft_match("LBRACKET", 1) and array_allowed:
                array = True
                self.next_token()
                self.expect("LBRACKET")
                
                while True:
                    expr = self.parse_expression()
                    dim.append(expr)

                    if self.soft_match("COMMA"):
                        self.next_token()
                        continue

                    if self.soft_match("RBRACKET"):
                        break

                    raise SyntaxError(f"Expected COMMA or RBRACKET, but found {self.current_token().kind} in line {self.get_current_line()}")


            var = Variable(var_name, ArrayType(dim, var_type) if array else var_type)

            expr_list.append(var)
            
            self.next_token()

            if self.soft_match("COMMA"):
                self.next_token()
                continue

            if self.reached_eol():
                break

            if self.soft_match("RPAREN") and inside_paren:
                break

            raise SyntaxError(f"Expected COMMA or NEWLINE, but found {self.current_token().kind} in line {self.get_current_line()}")

        return expr_list


    def parse_read(self, branch: _Union[Block, Program]):
        self.expect("READ")  # Skip "ΔΙΑΒΑΣΕ"

        
        var_list = []

        var_list = self._identifier_list()

        read = Read(var_list)

        self.expect_eol()
        log(f"From parse_read (parser_ast.py): Finished parsing the Read (ΔΙΑΒΑΣΕ) in line {self.current_token().line - 1}", tags=["r"])
        branch.body.append(read)


    def _expression_list(self, inside_paren: bool = False) -> _List[Expression]:
        """
        Creates a list of expressions.        
        """

        expr_list = []

        while self.current_token():
            # Process each part of the expression until a comma or newline or (if specified)
            # an RPAREN is encountered
            part_tokens = self.parse_expression()
            expr_list.append(part_tokens)

            # If the current token is a comma, skip it and continue
            if self.soft_match("COMMA"):
                self.next_token()
                continue

            if self.reached_eol():
                break

            if self.soft_match("RPAREN") and inside_paren:
                break

            raise SyntaxError(f"Expected COMMA or NEWLINE, but found {self.current_token().kind} in line {self.get_current_line()}")

        return expr_list


    def parse_write(self, branch: _Union[Block, Program]):
        self.next_token()  # Skip "ΓΡΑΨΕ"
        expr_list: _List[Expression] = []
        
        expr_list = self._expression_list()

        self.expect_eol()
        branch.body.append(Write(expr_list))


    def parse_assignment(self, branch: _Union[Block, Program]):
        # VALID_ASSIGNMENT_TOKENS = VALID_PROCESS_EXPRESSION_TOKENS
        # END_TOKENS = {"NEWLINE"}

        # Get the variable being assigned to
        token = self.current_token()  # The variable is the token before "<--"
        var_name = token.value
        self.next_token()  # Skip variable

        self.expect("ASSIGN")

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
        self.next_token()  # Skip "ΑΝ" or "ΑΛΛΙΩΣ_ΑΝ"
        condition_tokens = self.parse_expression()

        self.expect("THEN")
        self.expect_eol()
        self.next_line()

        then_branch = Block([])

        # Parse the body of the IF block
        self.parse_block(then_branch, ["ELSE", "ELSE_IF","END_IF"] + END_TOKENS_FOR_BLOCK, self.parse_block_dict)

        branches_node.append(Branch(condition_tokens, then_branch))

        # Handle ΑΛΛΙΩΣ_ΑΝ (else if) recursively
        while self.soft_match("ELSE_IF"):
            log(f"From parse_if (parser_ast.py): Current token in the loop is {self.current_token()}", tags=["pi"])
            # self.next_token() # parse if already skips the IF token (as well the ELSE_IF token)
            self.next_token()
            elif_condition_tokens = self.parse_expression()

            self.expect("THEN")
            self.expect_eol()
            self.next_line()
            temp_elif_branch = Block([])
            self.parse_block(temp_elif_branch, ["ELSE", "ELSE_IF","END_IF"] + END_TOKENS_FOR_BLOCK, self.parse_block_dict)  # Recursively parse the else-if block
            branches_node.append(Branch(elif_condition_tokens, temp_elif_branch))

        if not branches_node:
            raise SyntaxError(
                f"There are no branches in your if statement, in line {start_line}. Not even a condition, at least type one condition."
            )

        # Handle ΑΛΛΙΩΣ (else)
        else_branch = Block([])
        if self.soft_match("ELSE"):
            self.expect_token_alone("ELSE")
            self.next_line()
            self.parse_block(else_branch, ["END_IF"] + END_TOKENS_FOR_BLOCK, self.parse_block_dict)
        
        # self.expect_token_alone("END_IF")

        log(f"From parse_if (parser_ast.py): Expecting token {"END_IF"}", tags=["eta"])
        self.expect_tokens_line(1)
        if not self.soft_match("END_IF"):
            raise SyntaxError(
                f"Expected END_IF for the IF scope from line {start_line} but found {self.current_token().kind} instead."
            )
        log(f"From parse_if (parser_ast.py): Found {"END_IF"}", tags=["eta"])

        branch.body.append(
            If(
                branches=branches_node,
                else_branch=else_branch
            )
        )


    def parse_switch(self, branch: _Union[Block, Program]):
        self.found_else = False
        start_line = self.current_token().line # for better error messages
        self.expect("SWITCH")

        switch_expr = self.parse_expression() # ΕΠΙΛΕΞΕ expr
        self.expect_eol()
        
        branches_list = []
        else_block = Block([])

        self.next_line()
        while self.current_token().kind == "CASE":
            self.expect("CASE") # consumes the token
            case_block = Block([])
            case_expr = []

            if self.soft_match("ELSE"):
                self.found_else = True
                break

            while True:
                expr = self.parse_case_expression()
                case_expr.append(expr)

                if self.soft_match("COMMA"):
                    self.next_token()
                    continue

                if self.reached_eol():
                    break
                
                raise SyntaxError(f"Expected COMMA or NEWLINE, but found {self.current_token().kind} in line {self.get_current_line()}")

            self.next_line()
            self.parse_block(case_block, ["CASE", "END_SWITCH"] + END_TOKENS_FOR_BLOCK, self.parse_block_dict)

            branches_list.append(Branch(case_expr, case_block))

        if self.soft_match("ELSE"):
            self.expect("ELSE")
            self.expect_eol()
            self.next_line()
            self.parse_block(else_block, ["CASE", "END_SWITCH"] + END_TOKENS_FOR_BLOCK, self.parse_block_dict)

        log(f"From parse_if (parser_ast.py): Expecting token END_SWITCH", tags=["eta"])
        self.expect_tokens_line(1)
        if not self.soft_match("END_SWITCH"):
            raise SyntaxError(
                f"Expected END_SWITCH for the SWITCH scope from line {start_line} but found {self.current_token().kind} instead."
            )
        log(f"From parse_if (parser_ast.py): Found END_SWITCH", tags=["eta"])
        
        branch.body.append(Switch(switch_expr, branches_list, else_block))
        

    def parse_while(self, branch: _Union[Block, Program]):
        start_line = self.current_token().line
        self.next_token()
        condition = self.parse_expression()

        self.expect("REPEAT")
        self.expect_eol()
        self.next_line()

        while_branch = Block([])

        # Parse the body of the IF block
        self.parse_block(while_branch, ["END_LOOP"] + END_TOKENS_FOR_BLOCK, self.parse_block_dict)

        log(f"From parse_while (parser_ast.py): Expecting token {"END_LOOP"}", tags=["eta"])
        self.expect_tokens_line(1)
        if not self.soft_match("END_LOOP"):
            raise SyntaxError(
                f"Expected END_LOOP for the WHILE scope from line {start_line} but found {self.current_token().kind} instead."
            )
        log(f"From parse_while (parser_ast.py): Found {"END_LOOP"}", tags=["eta"])

        branch.body.append(
            While(
                condition=condition,
                body=while_branch
            )
        )


    def parse_for(self, branch: _Union[Block, Program]):
        start_line = self.current_token().line

        self.next_token() # skipping the token for
        
        self.match("IDENTIFIER")
        identifier = self.current_token()
        variable = Variable(identifier.value, None)

        self.next_token()
        self.expect("FROM")

        expr1 = self.parse_expression()

        self.expect("TO")

        expr2 = self.parse_expression()

        step = Number("1")
        if not self.reached_eol():
            self.expect("STEP")
            step = self.parse_expression()
        
        self.next_line()
        for_branch = Block([])
        self.parse_block(for_branch, ["END_LOOP"] + END_TOKENS_FOR_BLOCK, self.parse_block_dict)

        log("From parse_for (parser_ast.py): Expecting token 'END_LOOP'", tags=["eta"])
        self.expect_tokens_line(1)
        if not self.soft_match("END_LOOP"):
            raise SyntaxError(
                f"Expected END_LOOP for the FOR scope from line {start_line} but found {self.current_token().kind} instead."
            )
        log("From parse_for (parser_ast.py): Found 'END_LOOP'", tags=["eta"])

        branch.body.append(
            For(
                counter=variable,
                from_expr=expr1,
                to_expr=expr2,
                step=step,
                body=for_branch
            )
        )


    def parse_do(self, branch: _Union[Block, Program]):
        start_line = self.current_token().line

        self.expect_token_alone("START_LOOP")
        self.next_line()

        do_branch = Block([])
        self.parse_block(do_branch, ["UNTIL"] + END_TOKENS_FOR_BLOCK, self.parse_block_dict)


        log("From parse_do (parser_ast.py): Expecting token 'UNTIL'", tags=["eta"])
        if not self.soft_match("UNTIL"):
            raise SyntaxError(
                f"Expected END_LOOP for the FOR scope from line {start_line} but found {self.current_token().kind} instead."
            )
        log("From parse_do (parser_ast.py): Found 'UNTIL'", tags=["eta"])

        self.next_token()
        expr = self.parse_expression()

        self.expect_eol()

        branch.body.append(
            Do(
                condition=expr,
                body=do_branch
            )
        )


    def parse_call_procedure(self, branch: _Union[Block, Program]):
        self.expect("CALL")
        self.match("IDENTIFIER")
        procedure_name = self.current_token().value
        log(f"From parse_call_procedure (parser_ast.py): Found the procedure name: {procedure_name}", tags=["pcp"])

        self.next_token()
        self.expect("LPAREN")
        args = []

        if not self.soft_match("RPAREN"): # if there are no Parameters passed
            args = self._expression_list(inside_paren=True)

        self.expect("RPAREN")
        self.expect_eol()

        branch.body.append(CallProcedure(procedure_name, args))


    # def error_until(self, branch: _Union[Block, Program]) -> None:
    #     raise SyntaxError(
    #         f"Did not expect UNTIL here, did you forget to add START_LOOP? Line {self.get_current_line()}"
    #     )

    # __________________________________________________________________________________________________


    """
    Function:
    Returns a value, so it is treated as a value when it is called.
        returns INTEGER/FLOAT/CHARACTER/BOOLEAN
    
    PROCEDURE:
    Changes the variables that are passed when the procedure is finished. Possible implementation through reference.


    """

    def parse_function(self):
        self.expect("FUNCTION") # Skipping FUNCTION token

        self.match("IDENTIFIER")
        name = self.current_token()
        log(f"From parse_function (parser_ast.py): Found the name of the function {name}", tags=["pf"])

        self.next_token()
        self.expect("LPAREN")
        params = self._identifier_list(at_least_one_var=True, inside_paren=True)
        self.expect("RPAREN")
        log(f"From parse_function (parser_ast.py): Found the arguments of the function {params}", tags=["pf"])
        
        self.expect("COLON")
        
        token = self.current_token().kind
        if token not in TYPE_TABLE_FUNC:
            raise SyntaxError(
                f"Expected token in list INTEGER/REAL/CHARACTER/LOGICAL but found {self.current_token().value} instead. Line {self.get_current_line()}"
            )
        
        func_type = TYPE_TABLE_FUNC[token]
        log(f"From parse_function (parser_ast.py): Found the type of the function {func_type}", tags=["pf"])

        # self.next_line() # self.next_line() does a self.next_line() first thing.
        body = Block([])
        self.parse_variables_block(body)
        log(f"From parse_function (parser_ast.py): Done with the parsing of the variables block", tags=["pf"])

        function_block_dict = self.parse_block_dict.copy()
        
        for key in ["READ", "WRITE"]:
            function_block_dict.pop(key)

        self.parse_block(body, END_TOKENS_FOR_BLOCK, function_block_dict)
        log(f"From parse_function (parser_ast.py): Done with the parsing of the main block of the function", tags=["pf"])


        func = Function(
            name=name,
            params=params,
            body=body.body,
            func_type=func_type
        )

        return func

    
    def parse_procedure(self):
        self.expect("PROCEDURE") # Skipping PROCEDURE token

        self.match("IDENTIFIER")
        name = self.current_token()
        self.next_token()
        self.expect("LPAREN")
        params = self._identifier_list(at_least_one_var=True, inside_paren=True)
        self.expect("RPAREN")
        self.next_line()

        body = Block([])
        self.parse_variables_block(body)

        self.parse_block(body, END_TOKENS_FOR_BLOCK, self.parse_block_dict)

        proc = Procedure(
            name=name,
            params=params,
            body=body.body,
        )

        return proc