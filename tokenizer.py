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

import re

class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.greek_to_english = {
            'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E',
            'Ζ': 'Z', 'Η': 'H', 'Θ': 'TH', 'Ι': 'I', 'Κ': 'K',
            'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O',
            'Π': 'P', 'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y',
            'Φ': 'F', 'Χ': 'CH', 'Ψ': 'PS', 'Ω': 'W'
        }
        self.token_specification = [
            ('PROGRAM', r'ΠΡΟΓΡΑΜΜΑ'),      # Program declaration
            ('START', r'ΑΡΧΗ'),             # Program code starts, and variable declaration is finished
            ('VARIABLES', r'ΜΕΤΑΒΛΗΤΕΣ'),   # Variables section
            ('INTEGERS', r'ΑΚΕΡΑΙΕΣ'),      # Integer type
            ('CHARACTERS', r'ΧΑΡΑΚΤΗΡΕΣ'),  # Character type
            ('REAL', r'ΠΡΑΓΜΑΤΙΚΕΣ'),       # Real type
            ('LOGICAL', r'ΛΟΓΙΚΕΣ'),        # Logical type

            ('IF', r'ΑΝ'),                  # If statement
            ('THEN', r'ΤΟΤΕ'),              # Then keyword
            ('ELSE_IF', r'ΑΛΛΙΩΣ_ΑΝ'),      # Then keyword
            ('ELSE', r'ΑΛΛΙΩΣ'),            # Else keyword
            ('END_IF', r'ΤΕΛΟΣ_ΑΝ'),        # End if
            
            ('FOR', r'ΓΙΑ'),
            ('FROM', r'ΑΠΟ'),
            ('TO', r'ΜΕΧΡΙ'),
            ('STEP', r'ΜΕ_ΒΗΜΑ'),

            ('WHILE', r'ΟΣΟ'),
            ('REPEAT', r'ΕΠΑΝΑΛΑΒΕ'),

            ('END_PROGRAM', r'ΤΕΛΟΣ_ΠΡΟΓΡΑΜΜΑΤΟΣ'),

            ('ASSIGN', r'<--'),             # Assignment operator
            ('READ', r'ΔΙΑΒΑΣΕ'),           # Read input
            ('WRITE', r'ΓΡΑΨΕ'),            # Write output


            ('NEQ', r'(?<!<)<>(?!>)'),      # Match '<>' only if not part of a larger token
            ('GTE', r'>='),                 # Greater than or equal to
            ('LTE', r'<='),                 # Less than or equal to
            ('GT', r'>'),                   # Greater than
            ('LT', r'<'),                   # Less than
            ('EQ', r'='),                   # Equal to
            
            ('NOT', r'ΟΧΙ'),
            ('AND', r'ΚΑΙ'),
            ('OR', r'Ή'),

            ('PROCEDURE', r'ΔΙΑΔΙΚΑΣΙΑ'),
            ('FUNCTION', r'ΣΥΝΑΡΤΗΣΗ'),
            ('BUILTIN_FUNCTION', r'Α_Μ|Α_Τ|Τ_Ρ'), # It might be better to use multiple different tokens for each built in function

            ('STRING', r'"[^"]*"'),
            ('FLOAT', r'-?\d+\.\d+'),
            ('NUMBER', r'\d+'), # The + in regex means that all the sequential numebrs are counted as one
            ('BOOLEAN', r'ΑΛΗΘΗΣ|ΨΕΥΔΗΣ'),

            ('COLON', r':'),
            ('COMMA', r','),

            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('PLUS', r'\+'),
            ('MINUS', r'\-'),
            ('MUL', r'\*'),
            ('FDIV', r'\/'),
            ('POW', r'\^'),
            ('MOD', r'MOD'),
            ('IDIV', r'DIV'),

            ('GREEK_IDENTIFIER', r'[Α-Ω_][Α-Ω0-9_]*'),  # Greek identifiers
            ('ENGLISH_IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # English identifiers

            ('COMMENT', r'!.*'),
            ('WHITESPACE', r'[ \t]+'),
            ('NEWLINE', r'\n'),
            ('MISMATCH', r'.'),             # Any other character
        ]
        self.token = [i[0] for i in self.token_specification]

    def tokenize(self):
        token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in self.token_specification)
        program_name_expected = False  # Flag to track if the next token is the program name

        for match in re.finditer(token_regex, self.code):
            kind = match.lastgroup
            value = match.group()

            if kind in ['WHITESPACE', 'COMMENT']:
                continue  # Skip whitespace and comments
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Unexpected character: {value}")
            elif program_name_expected:
                # Handle the program name
                if kind in ['GREEK_IDENTIFIER', 'ENGLISH_IDENTIFIER']:
                    kind = 'PROGRAM_NAME'
                    value = ''.join(self.greek_to_english.get(char, char) for char in value)
                else:
                    raise SyntaxError(f"Expected a program name after 'ΠΡΟΓΡΑΜΜΑ', but got '{value}'")
                program_name_expected = False  # Reset the flag
            elif kind == 'PROGRAM':
                program_name_expected = True  # Set the flag to expect a program name
            elif kind == 'GREEK_IDENTIFIER':
                # Translate Greek variable names to English equivalents with a prefix
                value = 'gr_' + ''.join(self.greek_to_english.get(char, char) for char in value)
                kind = 'IDENTIFIER'  # Normalize to shared IDENTIFIER token
            elif kind == 'ENGLISH_IDENTIFIER':
                # Prefix English variable names with a distinct prefix
                value = 'en_' + value
                kind = 'IDENTIFIER'  # Normalize to shared IDENTIFIER token
            elif kind == 'BOOLEAN':
                value = 'true' if 'ΑΛΗΘΗΣ' else 'false'

            self.tokens.append(tuple([kind, value]))

        self._validate_order_and_uniqueness()

        print(self.tokens)

        return self.tokens
    
    
    def _validate_order_and_uniqueness(self):
        """
        Enforce:
         - 'START' must appear exactly once
         - PROGRAM, VARIABLES, INTEGERS, CHARACTERS, REAL, LOGICAL must appear at most once
           and (if present) must be located before 'START'
        """
        must_be_before_start = ['PROGRAM', 'VARIABLES', 'INTEGERS', 'CHARACTERS', 'REAL', 'LOGICAL']
        positions = {}
        for idx, (kind, _) in enumerate(self.tokens):
            positions.setdefault(kind, []).append(idx)

        # START must appear exactly once
        start_positions = positions.get('START', [])
        if len(start_positions) != 1:
            raise SyntaxError("Token 'ΑΡΧΗ' (START) must appear exactly once")
        start_positions = positions.get('PROGRAM', [])
        if len(start_positions) != 1:
            raise SyntaxError("Token 'ΠΡΟΓΡΑΜΜΑ' (PROGRAM) must appear exactly once")


        start_idx = start_positions[0]

        # Each token in must_be_before_start must appear at most once and before START if present
        for tk in must_be_before_start:
            if tk in positions:
                if len(positions[tk]) != 1:
                    raise SyntaxError(f"Token '{tk}' must appear at most once")
                if positions[tk][0] > start_idx:
                    raise SyntaxError(f"Token '{tk}' must appear before 'ΑΡΧΗ' (START)")