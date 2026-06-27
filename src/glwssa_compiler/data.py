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

from dataclasses import dataclass

# A token should never be changed
@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    original_value: str
    line: int
    column: int
    col_start: int
    col_end: int


@dataclass(frozen=True)
class Scope:
    scope: str 
    token: Token
    recoverable: bool = True


# Dataclasses for error diagnostics ____________________________________
@dataclass(frozen=True)
class Diagnostic: ...


@dataclass(frozen=True)
class Expected(Diagnostic):
    expected: str
    got: Token
    context: str = ""
    translate: bool = True


@dataclass(frozen=True)
class ExpectedOneToken(Diagnostic):
    ...


@dataclass(frozen=True)
class ScopeNotClosed(Diagnostic):
    found: Token
    expected: Scope


@dataclass(frozen=True)
class CommandOutOfPlace(Diagnostic):
    command: Token

# For the Lexer ________________________________________________________

def gsk(keyword: str) -> str:
    """
    Glwssa Standalone Keyword function.
    
    :param keyword: the standalone keyword
    :type keyword: str
    :return: returns a regex expression that only detects the standalone keyword
    :rtype: str
    """
    return f"(?<![A-Za-zΑ-Ωα-ω0-9_]){keyword}(?![A-Za-zΑ-Ωα-ω0-9_])"

class InfoTokens:
        token_specification = [
            ('PROGRAM', fr'{gsk('ΠΡΟΓΡΑΜΜΑ')}'),      # Program declaration
            ('START', fr'{gsk('ΑΡΧΗ')}'),             # Program code starts, and variable declaration is finished
            ('CONSTANTS', fr'{gsk('ΣΤΑΘΕΡΕΣ')}'),
            ('VARIABLES', fr'{gsk('ΜΕΤΑΒΛΗΤΕΣ')}'),   # Variables section
            ('INTEGERS', fr'{gsk('ΑΚΕΡΑΙΕΣ')}'),      # Integer type
            ('CHARACTERS', fr'{gsk('ΧΑΡΑΚΤΗΡΕΣ')}'),  # Character type
            ('REALS', fr'{gsk('ΠΡΑΓΜΑΤΙΚΕΣ')}'),       # Real type
            ('LOGICALS', fr'{gsk('ΛΟΓΙΚΕΣ')}'),        # Logical type

            ('INTEGER', fr'{gsk('ΑΚΕΡΑΙΑ')}'),      # Integer type
            ('CHARACTER', fr'{gsk('ΧΑΡΑΚΤΗΡΑΣ')}'),  # Character type
            ('REAL', fr'{gsk('ΠΡΑΓΜΑΤΙΚΗ')}'),       # Real type
            ('LOGICAL', fr'{gsk('ΛΟΓΙΚΗ')}'),        # Logical type

            ('IF', fr'{gsk('ΑΝ')}'),                  # If statement
            ('THEN', fr'{gsk('ΤΟΤΕ')}'),              # Then keyword
            ('ELSE_IF', fr'{gsk('ΑΛΛΙΩΣ_ΑΝ')}'),      # Then keyword
            ('ELSE', fr'{gsk('ΑΛΛΙΩΣ')}'),            # Else keyword
            ('END_IF', fr'{gsk('ΤΕΛΟΣ_ΑΝ')}'),        # End if

            ('SWITCH', fr'{gsk('ΕΠΙΛΕΞΕ')}'),
            ('CASE', fr'{gsk('ΠΕΡΙΠΤΩΣΗ')}'),
            ('END_SWITCH', fr'{gsk('ΤΕΛΟΣ_ΕΠΙΛΟΓΩΝ')}'),
            
            ('FOR', fr'{gsk('ΓΙΑ')}'),
            ('FROM', fr'{gsk('ΑΠΟ')}'),
            ('TO', fr'{gsk('ΜΕΧΡΙ')}'),
            ('STEP', fr'{gsk('ΜΕ_ΒΗΜΑ')}'),

            ('WHILE', fr'{gsk('ΟΣΟ')}'),
            ('REPEAT', fr'{gsk('ΕΠΑΝΑΛΑΒΕ')}'),
            ('END_LOOP', fr'{gsk('ΤΕΛΟΣ_ΕΠΑΝΑΛΗΨΗΣ')}'),        # End if

            ('START_LOOP', fr'{gsk('ΑΡΧΗ_ΕΠΑΝΑΛΗΨΗΣ')}'),
            ('UNTIL', fr'{gsk('ΜΕΧΡΙΣ_ΟΤΟΥ')}'),

            ('END_PROGRAM', fr'{gsk('ΤΕΛΟΣ_ΠΡΟΓΡΑΜΜΑΤΟΣ')}'),

            ('ASSIGN', r'<-'),             # Assignment operator
            ('READ', fr'{gsk('ΔΙΑΒΑΣΕ')}'),           # Read input
            ('WRITE', fr'{gsk('ΓΡΑΨΕ')}'),            # Write output


            ('NEQ', r'(?<!<)<>(?!>)'),      # Match '<>' only if not part of a larger token
            ('GTE', r'>='),                 # Greater than or equal to
            ('LTE', r'<='),                 # Less than or equal to
            ('GT', r'>'),                   # Greater than
            ('LT', r'<'),                   # Less than
            ('EQ', r'='),                   # Equal to
            
            ('NOT', fr'{gsk('ΟΧΙ')}'),
            ('AND', fr'{gsk('ΚΑΙ')}'),
            ('OR', fr'{gsk('Ή')}|{gsk('Η')}'),

            ('CALL', fr'{gsk('ΚΑΛΕΣΕ')}'),
            ('PROCEDURE', fr'{gsk('ΔΙΑΔΙΚΑΣΙΑ')}'),
            ('END_PROCEDURE', fr'{gsk('ΤΕΛΟΣ_ΔΙΑΔΙΚΑΣΙΑΣ')}'),

            ('FUNCTION', fr'{gsk('ΣΥΝΑΡΤΗΣΗ')}'),
            ('END_FUNCTION', fr'{gsk('ΤΕΛΟΣ_ΣΥΝΑΡΤΗΣΗΣ')}'),

            ('BUILTIN_FUNCTION', fr'{gsk('Α_Μ')}|{gsk('Τ_Ρ')}|{gsk('Α_Τ')}'), # It might be better to use multiple different tokens for each built in function

            ('STRING', r'"[^"]*"|\'[^\']*\''),
            ('INVALID_STRING_1', r'"[^"]*\''),            
            ('INVALID_STRING_2', r'\'[^\']*"'),  
            ('PERIOD', r'\.\.'),
            ('FLOAT', r'-?\d+\.\d+'),
            ('NUMBER', r'\d+'), # The + in regex means that all the sequential numebrs are counted as one
            ('BOOLEAN', fr'{gsk('ΑΛΗΘΗΣ')}|{gsk('ΨΕΥΔΗΣ')}'),

            ('COLON', r':'),
            ('COMMA', r','),

            ('LBRACKET', r'\['), # for arrays
            ('RBRACKET', r'\]'),

            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('PLUS', r'\+'),
            ('MINUS', r'\-'),
            ('MUL', r'\*'),
            ('FDIV', r'\/'),
            ('POW', r'\^'),
            ('MOD', fr'{gsk('MOD')}'),
            ('IDIV', fr'{gsk('DIV')}'),

            ('GREEK_IDENTIFIER', r'[α-ωΑ-Ω_][α-ωΑ-Ω0-9_]*'),  # Greek identifiers
            ('ENGLISH_IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # English identifiers

            ('COMMENT', r'!.*'),
            ('WHITESPACE', r'[ \t]+'),
            ('NEWLINE', r'\n'),
            ('MISMATCH', r'.'),             # Any other character
        ]
        tokens_type = [i[0] for i in token_specification]
