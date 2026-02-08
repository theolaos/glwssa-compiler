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

from .tokens import Token, Scope

from typing import Callable as _Callable
from typing import Union as _Union


class ErrorStack:
    def __init__(self):
        self.code_file: str = ""
        
        self.parser_errors: dict[int, _Callable[[],None]] = {
            1 : self.expected,
            2 : self.expected_one_token,
            3 : self.expected_token_alone,
            4 : self.scope_not_closed,
            5 : self.command_out_of_place,
            6 : self.empty_branches,
        }
        self.error_msgs_dict: dict[str, dict] = {
            "P" : ...
        }

        self.error_stack = []


    def push(self, error_code: str) -> None:
        """
        pushes an error/warning to the error stack
        """

    def print_errors(self) -> None:
        ...


    def print_warnings(self) -> None:
        ...


    def print_notes(self) -> None:
        ...


    def expected(self, expected: str, got: Token,) -> None:
        ...


    def expected_one_token(self, lparen_col: int, line: int) -> None:
        ...


    def expected_token_alone(self, expected: Token) -> None:
        """
        :param expected: the type is a Token, because the error stack needs the position data.
        """
        ...


    def scope_not_closed(self, scope: Scope, end_scope_error_line: int) -> None:
        ...

    
    def command_out_of_place(self, command: Token) -> None:
        ...

    
    def empty_branches(self, if_scope: Scope) -> None:
        ...