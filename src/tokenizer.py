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

import re

from dataclasses import dataclass

from .log import log
from .tokens import Token


def gsk(keyword: str) -> str:
    """
    Glwssa Standalone Keyword function.
    
    :param keyword: the standalone keyword
    :type keyword: str
    :return: returns a regex expression that only detects the standalone keyword
    :rtype: str
    """
    return f"(?<![A-Za-zΑ-Ωα-ω0-9_]){keyword}(?![A-Za-zΑ-Ωα-ω0-9_])"


class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.greek_to_english = {
            'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E',
            'Ζ': 'Z', 'Η': 'H', 'Θ':'TH', 'Ι': 'I', 'Κ': 'K',
            'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O',
            'Π': 'P', 'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y',
            'Φ': 'F', 'Χ':'CH', 'Ψ':'PS', 'Ω': 'W',
            'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e',
            'ζ': 'z', 'η': 'h', 'θ':'th', 'ι': 'i', 'κ': 'k',
            'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o',
            'π': 'p', 'ρ': 'r', 'σ': 's', 'τ': 't', 'υ': 'y',
            'φ': 'f', 'χ':'ch', 'ψ':'ps', 'ω': 'w',
            # 'ί':'Ti', 'ή':'Th', 'ό':'To', 'ύ':'Tu', 'έ':'Te', 'ά':'Ta', 'ώ':'Tw', 
            # 'Ί':'tI', 'Ή':'tH', 'Ό':'tO', 'Ύ':'tU', 'Έ':'tE', 'Ά':'tA', 'Ώ':'tW'
        }
        self.token_specification = [
            ('PROGRAM', fr'{gsk('ΠΡΟΓΡΑΜΜΑ')}'),      # Program declaration
            ('START', fr'{gsk('ΑΡΧΗ')}'),             # Program code starts, and variable declaration is finished
            ('CONSTANTS', fr'{gsk('ΣΤΑΘΕΡΕΣ')}'),
            ('VARIABLES', fr'{gsk('ΜΕΤΑΒΛΗΤΕΣ')}'),   # Variables section
            ('INTEGERS', fr'{gsk('ΑΚΕΡΑΙΕΣ')}'),      # Integer type
            ('CHARACTERS', fr'{gsk('ΧΑΡΑΚΤΗΡΕΣ')}'),  # Character type
            ('REAL', fr'{gsk('ΠΡΑΓΜΑΤΙΚΕΣ')}'),       # Real type
            ('LOGICAL', fr'{gsk('ΛΟΓΙΚΕΣ')}'),        # Logical type

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
        self.token = [i[0] for i in self.token_specification]


    def tokenize_with_lines(self):
        token_regex = '|'.join(
            f'(?P<{pair[0]}>{pair[1]})'
            for pair in self.token_specification
        )

        program_name_expected = False
        token_lines = []

        for line_no, line in enumerate(self.code.splitlines(), start=1):
            line_tokens = []
            print(line, line_no)

            column = 0
            for match in re.finditer(token_regex, line):
                kind = match.lastgroup
                value = match.group()
                # log(kind, value, tags=["mtok"])

                if kind in {'WHITESPACE', 'COMMENT'}:
                    continue

                if kind == 'MISMATCH':
                    raise SyntaxError(f"Unexpected character '{value}' on line {line_no}")

                if kind == "INVALID_STRING_1":
                    raise SyntaxError(f"Unexpected character \' on line {line_no} for string {value}")
                
                if kind == "INVALID_STRING_2":
                    raise SyntaxError(f"Unexpected character \" on line {line_no} for string {value}")

                if program_name_expected:
                    if kind == 'GREEK_IDENTIFIER':
                        kind = 'PROGRAM_NAME'
                        value = 'gr_' + ''.join(self.greek_to_english.get(c, c) for c in value)
                        program_name_expected = False
                    elif kind ==  'ENGLISH_IDENTIFIER':
                        kind = 'PROGRAM_NAME'
                        value = 'en_' + value
                        program_name_expected = False
                    else:
                        raise SyntaxError(f"Expected program name after 'ΠΡΟΓΡΑΜΜΑ' on line {line_no}")

                elif kind == 'PROGRAM':
                    program_name_expected = True

                elif kind == 'GREEK_IDENTIFIER':
                    value = 'gr_' + ''.join(self.greek_to_english.get(c, c) for c in value)
                    kind = 'IDENTIFIER'

                elif kind == 'ENGLISH_IDENTIFIER':
                    value = 'en_' + value
                    kind = 'IDENTIFIER'

                elif kind == 'BOOLEAN':
                    value = 'true' if value == 'ΑΛΗΘΗΣ' else 'false'
                line_tokens.append(Token(kind, value, line_no, column, match.start(), match.end()-1))
                column += 1

            if line_tokens:
                token_lines.append(line_tokens)
        
        for line in token_lines:
            log(line, tags=['atok'])
        self.tokens = token_lines
        self._validate_order_and_uniqueness()

        return token_lines

    def _validate_order_and_uniqueness(self):
        must_be_before_start = [
            'PROGRAM', 'VARIABLES', 'INTEGERS',
            'CHARACTERS', 'REAL', 'LOGICAL'
        ]

        # kind -> list of (line_idx, token_idx)
        positions = {}

        for line_idx, line in enumerate(self.tokens):
            for token_idx, token in enumerate(line):
                positions.setdefault(token.kind, []).append((line_idx, token_idx))

        # PROGRAM must appear exactly once
        program_positions = positions.get('PROGRAM', [])
        if len(program_positions) != 1:
            raise SyntaxError("Token 'ΠΡΟΓΡΑΜΜΑ' (PROGRAM) must appear exactly once")

        # START must appear exactly once
        start_positions = positions.get('START', [])
        if len(start_positions) != 1:
            raise SyntaxError("Token 'ΑΡΧΗ' (START) must appear exactly once")

        start_line, start_col = start_positions[0]

        # Tokens that must be before START
        for tk in must_be_before_start:
            if tk in positions:
                if len(positions[tk]) != 1:
                    raise SyntaxError(f"Token '{tk}' must appear at most once")

                tk_line, tk_col = positions[tk][0]

                # Compare position to START
                if (tk_line > start_line) or (
                    tk_line == start_line and tk_col > start_col
                ):
                    raise SyntaxError(
                        f"Token '{tk}' must appear before 'ΑΡΧΗ' (START)"
                    )