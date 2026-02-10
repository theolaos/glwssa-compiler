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


from .data import *
from .log import log

from typing import Callable as _Callable
from typing import Union as _Union

import traceback


end_matches_sub_scopes = {
    "END_IF" : "IF",
    "END_LOOP" : "LOOP",
    "END_SWITCH" : "SWITCH",
    "END_PROGRAM" : "PROGRAM",
    "END_PROCEDURE" : "PROCEDURE",
    "END_FUNCTION" : "FUNCTION",
    "EOF" : "EOF"
}

end_matches_sub_scopes_msg = {
    "IF" : "ΤΕΛΟΣ_ΑΝ",
    "FOR" : "ΤΕΛΟΣ_ΕΠΑΝΑΛΗΨΗΣ",
    "WHILE" : "ΤΕΛΟΣ_ΕΠΑΝΑΛΗΨΗΣ",
    "START_LOOP" : "ΜΕΧΡΙΣ_ΟΤΟΥ",
    "SWITCH" : "ΤΕΛΟΣ_ΕΠΙΛΟΓΩΝ",
}

def DebugIssue():
    """
    Small abstraction for the message below, for every instance of an Internal Compiler Error.
    """
    print("Τρέξε τον κώδικα σου με tags='all' exclude_tags='mtok' και έπειτα στείλε το '.log' αρχείο μαζί με τον", end=" ")
    print("κώδικα σου σε ένα νέο Issue στο github page του glwssa-compiler - https://github.com/theolaos/glwssa-compiler")    


def add_arrows(code_file: list[str], line: int, cs: int, ce: int) -> None:
    """
    Prints a line of code which is being highlighted with arrows below
    
    :param code_file: 
    :type code_file: list[str]
    :param line: 
    :type line: int
    :param cs: Column Start
    :type cs: int
    :param ce: Column end 
    :type ce: int
    """
    log(f"line: {line}, code_file: {len(code_file)}", tags=["de"])
    s = f"γρ.: {line} ->"
    print(s, code_file[line-1])
    print(" "*len(s),f"{"~" * cs + "^" * (ce - cs + 1)}")


class ErrorStack:
    def __init__(self, code_file: list[str]):
        self.code_file: list[str] = code_file
        log(f"The length of the code file is {len(self.code_file)} lines", tags=["de"])
        
        self.parser_errors: dict[Diagnostic, _Callable[[Diagnostic], None]] = {
            Expected : self.expected,
            ExpectedOneToken : self.expected_one_token,
            3 : self.expected_token_alone,
            ScopeNotClosed : self.scope_not_closed,
            5 : self.command_out_of_place,
            6 : self.empty_branches,
        }


        self.errors_stack: list[Diagnostic] = []
        self.warnings_stack: list[Diagnostic] = []
        self.notes_stack: list[Diagnostic] = []


    def push(self, diag: Diagnostic) -> None:
        """
        pushes an error/warning to the error stack
        """
        self.errors_stack.append(diag)


    def print_errors(self) -> None:
        log(self.errors_stack, tags=["de"])
        for error in self.errors_stack:
            try:
                self.parser_errors[type(error)](error)
            except KeyError:
                error_traceback = traceback.format_exc()
                log(error_traceback, ["e"], "both")
                print("ΣΦΑΛΜΑ <IZ90> : Εσωτερικό σφάλμα διαχείρισης σφαλμάτων του Διαμεταγλωττιστή.")
                DebugIssue()


    def print_warnings(self) -> None:
        ...


    def print_notes(self) -> None:
        ...


    def expected(self, diag: Expected) -> None:
        ...


    def expected_one_token(self, diag: ExpectedOneToken) -> None:
        ...


    def expected_token_alone(self, err:str, expected: Token) -> None:
        """
        :param expected: the type is a Token, because the error stack needs the position data.
        """
        ...


    def scope_not_closed(self, diag: ScopeNotClosed) -> None:
        found_token = diag.found
        target_token = diag.expected.token
        end_line = diag.found.line

        print(f"ΣΦΑΛΜΑ <GP04> γρ.{end_line}. Ο βρόγχος '{target_token.value}', στην γραμμή {target_token.line}, έκλεισε λανθασμένα στην γραμμή {end_line}.")
        print(f"Περίμενα '{target_token.value}' αλλά βρήκα '{found_token.value}' στην γραμμή: {end_line}.")
        
        add_arrows(self.code_file, target_token.line, target_token.col_start, target_token.col_end)
        add_arrows(self.code_file, end_line, found_token.col_start, found_token.col_end)

        try:
            print(f"Συμβουλή: Άλλαξε το {found_token.value} σε {end_matches_sub_scopes_msg[found_token.kind]}.")
        except KeyError:
            ...
    
    def command_out_of_place(self, diag: Diagnostic) -> None:
        ...

    
    def empty_branches(self, err:str, if_scope: Scope) -> None:
        ...