import re

class Tokenizer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.token_specification = [
            ('PROGRAM', r'ΠΡΟΓΡΑΜΜΑ'),      # Program declaration
            ('VARIABLES', r'ΜΕΤΑΒΛΗΤΕΣ'),   # Variables section
            ('INTEGERS', r'ΑΚΕΡΑΙΕΣ'),      # Integer type
            ('CHARACTERS', r'ΧΑΡΑΚΤΗΡΕΣ'),  # Character type
            ('REAL', r'ΠΡΑΓΜΑΤΙΚΕΣ'),       # Real type
            ('LOGICAL', r'ΛΟΓΙΚΕΣ'),         # Logical type
            ('IF', r'ΑΝ'),                  # If statement
            ('THEN', r'ΤΟΤΕ'),              # Then keyword
            ('END_IF', r'ΤΕΛΟΣ_ΑΝ'),        # End if
            ('END_PROGRAM', r'ΤΕΛΟΣ_ΠΡΟΓΡΑΜΜΑΤΟΣ'),  # End program
            ('ASSIGN', r'<--'),             # Assignment operator
            ('READ', r'ΔΙΑΒΑΣΕ'),           # Read input
            ('WRITE', r'ΓΡΑΨΕ'),            # Write output
            ('COLON', r':'),                # Colon
            ('COMMA', r','),                # Comma
            ('GT', r'>'),                   # Greater than
            ('LT', r'<'),                   # Less than
            ('EQ', r'='),                   # Equal to
            ('NEQ', r'<>'),                 # Not equal to
            ('GTE', r'>='),                 # Greater than or equal to
            ('LTE', r'<='),                 # Less than or equal to
            ('IDENTIFIER', r'[Α-Ω_]\w*'),   # Identifiers (Greek letters)
            ('STRING', r'"[^"]*"'),         # String literals
            ('NUMBER', r'\d+'),             # Numbers
            ('FLOAT', r'\d+\,\d+'),         # Floating point numbers
            ('BOOLEAN', r'ΑΛΗΘΗΣ|ΨΕΥΔΗΣ'),  # Boolean values
            ('COMMENT', r'!.*'),            # Single line comments
            ('OP', r'[+\-*/]'),             # Arithmetic operators
            ('WHITESPACE', r'[ \t]+'),      # Skip spaces and tabs
            ('NEWLINE', r'\n'),             # Line endings
            ('MISMATCH', r'.'),             # Any other character
        ]
        self.token = [i[0] for i in self.token_specification]

    def tokenize(self):
        token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in self.token_specification)
        for match in re.finditer(token_regex, self.code):
            kind = match.lastgroup
            value = match.group()
            if kind in ['WHITESPACE', 'COMMENT']:
                continue  # Skip whitespace and newlines
            elif kind == 'MISMATCH':
                raise SyntaxError(f"Unexpected character: {value}")
            self.tokens.append((kind, value))
        return self.tokens