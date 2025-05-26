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
            ('VARIABLES', r'ΜΕΤΑΒΛΗΤΕΣ'),   # Variables section
            ('INTEGERS', r'ΑΚΕΡΑΙΕΣ'),      # Integer type
            ('CHARACTERS', r'ΧΑΡΑΚΤΗΡΕΣ'),  # Character type
            ('REAL', r'ΠΡΑΓΜΑΤΙΚΕΣ'),       # Real type
            ('LOGICAL', r'ΛΟΓΙΚΕΣ'),         # Logical type

            ('IF', r'ΑΝ'),                  # If statement
            ('THEN', r'ΤΟΤΕ'),               # Then keyword
            ('ELSE_IF', r'ΑΛΛΙΩΣ_ΑΝ'),               # Then keyword
            ('ELSE', r'ΑΛΛΙΩΣ'),             # Else keyword
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

            ('COLON', r':'),
            ('COMMA', r','),

            ('NEQ', r'(?<!<)<>(?!>)'),      # Match '<>' only if not part of a larger token
            ('GT', r'>'),                   # Greater than
            ('LT', r'<'),                   # Less than
            ('EQ', r'='),                   # Equal to
            ('GTE', r'>='),                 # Greater than or equal to
            ('LTE', r'<='),                 # Less than or equal to
            
            ('AND', r'ΚΑΙ'),
            ('OR', r'Ή'),
            ('NOT', r'ΟΧΙ'),

            ('PROCEDURE', r'ΔΙΑΔΙΚΑΣΙΑ'),
            ('FUNCTION', r'ΣΥΝΑΡΤΗΣΗ'),   

            ('GREEK_IDENTIFIER', r'[Α-Ω_][Α-Ω0-9_]*'),  # Greek identifiers
            ('ENGLISH_IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),  # English identifiers

            ('STRING', r'"[^"]*"'),
            ('NUMBER', r'-?\d+'),
            ('FLOAT', r'-?\d+\,\d+'),
            ('BOOLEAN', r'ΑΛΗΘΗΣ|ΨΕΥΔΗΣ'),

            ('OP', r'[+\-*/]'),             # Arithmetic operators
            ('MOD', r'MOD'),                  # Modulus operator
            ('DIV', r'DIV'),                  # Integer division operator

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
    
            self.tokens.append((kind, value))
    
        return self.tokens