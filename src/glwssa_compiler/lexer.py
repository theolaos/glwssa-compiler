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

from .log import log
from .data import Token, InfoTokens


class Lexer:
    def __init__(self, code, error_stack):
        self.error_stack = error_stack

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


    def tokenize_with_lines(self):
        token_regex = '|'.join(
            f'(?P<{pair[0]}>{pair[1]})'
            for pair in InfoTokens.token_specification
        )

        program_name_expected = False
        token_lines: list[list[Token]] = []

        for line_no, line in enumerate(self.code.splitlines(), start=1):
            line_tokens = []
            log(line, line_no, tags=["lines"])

            column = 0
            for match in re.finditer(token_regex, line):
                kind = match.lastgroup
                original_value = match.group()
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
                line_tokens.append(Token(kind, value, original_value, line_no, column, match.start(), match.end()-1))
                column += 1

            if line_tokens:
                token_lines.append(line_tokens)
        
        for line in token_lines:
            log(line, tags=['atok'])
        self.tokens = token_lines

        return token_lines