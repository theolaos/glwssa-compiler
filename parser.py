class Parser:
    def __init__(self, tokens, token):
        self.tokens = tokens
        self.current_token_index = 0
        self.cpp_code = []
        self.program_name = "a"
        self.greek_to_english = {
            'Α': 'A', 'Β': 'B', 'Γ': 'G', 'Δ': 'D', 'Ε': 'E',
            'Ζ': 'Z', 'Η': 'H', 'Θ': 'TH', 'Ι': 'I', 'Κ': 'K',
            'Λ': 'L', 'Μ': 'M', 'Ν': 'N', 'Ξ': 'X', 'Ο': 'O',
            'Π': 'P', 'Ρ': 'R', 'Σ': 'S', 'Τ': 'T', 'Υ': 'Y',
            'Φ': 'F', 'Χ': 'CH', 'Ψ': 'PS', 'Ω': 'W'
        }
        self.operator_mapping = {
            'NEQ': '!=',  # Not equal
            'EQ': '==',   # Equal
            'GT': '>',    # Greater than
            'LT': '<',    # Less than
            'GTE': '>=',  # Greater than or equal
            'LTE': '<=',   # Less than or equal
            'AND': '&&',  # Logical AND
            'OR': '||',   # Logical OR
            'NOT': '!',   # Logical NOT
            'MOD': '%',   # Modulus operator
            'DIV': '//',  # Division operator
        }


    def current_token(self, index=0):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index+index]
        return None  # Return None if out of bounds


    def next_token(self):
        self.current_token_index += 1


    def process_expression(self, valid_tokens, end_tokens):
        """
        Process an expression by iterating over tokens until an end token is encountered.

        :param valid_tokens: A set of valid token types for the expression.
        :param end_tokens: A set of token types that indicate the end of the expression.
        :return: A list of processed tokens for the expression.
        """
        expression_tokens = []

        while self.current_token() and self.current_token()[0] not in end_tokens:
            token_type, token_value = self.current_token()
            if token_type not in valid_tokens:
                raise SyntaxError(f"Unexpected token '{token_value}' in expression")
            
            if token_type == 'FLOAT':
                # Convert Greek float format (e.g., 2,5) to C++ format (e.g., 2.5)
                token_value = token_value.replace(',', '.')
            elif token_type in self.operator_mapping:
                # Map operators using the operator_mapping dictionary
                token_value = self.operator_mapping[token_type]

            expression_tokens.append(token_value)
            self.next_token()  # Move to the next token

        return expression_tokens


    def parse(self):
        while self.current_token_index < len(self.tokens):
            token = self.current_token()
            if token is None:
                break  # Exit if no more tokens
            token_type, token_value = token
            if token_type == 'PROGRAM':
                self.parse_program()
            elif token_type == 'VARIABLES':
                self.parse_variables()
                print("Parsing variables...")
            elif token_type == 'READ':
                self.parse_read()
            elif token_type == 'WRITE':
                self.parse_write()
            elif token_type == 'ASSIGN':
                self.parse_assignment()
            elif token_type == 'IF':
                self.parse_if()
            elif token_type == 'END_PROGRAM':
                print("End of program reached.")
                self.cpp_code.append("return 0;\n}")
                self.next_token()  # Advance to the next token
            else:
                self.next_token()  # Skip unhandled tokens

            # Stop parsing if the current token index reaches the last token
            if self.current_token_index >= len(self.tokens):
                break

        return "\n".join(self.cpp_code), self.program_name
    

    def parse_block(self, end_tokens):
        while self.current_token() and self.current_token()[0] not in end_tokens:
            token_type, _ = self.current_token()
            if token_type == 'WRITE':
                self.parse_write()
            elif token_type == 'READ':
                self.parse_read()
            elif token_type == 'IF':
                self.parse_if()  # Handle nested if statements
            elif token_type == 'ASSIGN':
                self.parse_assignment()
            else:
                self.next_token()  # Skip unhandled tokens

    def parse_program(self):
        self.cpp_code.append(f"#include <iostream>\n\nint main() {{")
        self.next_token()  # Skip 'ΠΡΟΓΡΑΜΜΑ'
        if not self.current_token() or self.current_token()[0] != 'PROGRAM_NAME':
            raise SyntaxError("Expected program name after 'ΠΡΟΓΡΑΜΜΑ'")
        _, self.program_name = self.current_token()


    def parse_variables(self):
        while not(self.current_token() and self.current_token()[0] not in ['NEWLINE','VARIABLES']):
            self.next_token()

        print(self.current_token(), '...')
        VALID_VARIABLE_TYPES = {'INTEGERS', 'CHARACTERS', 'REAL', 'LOGICAL'}

        while self.current_token() and self.current_token()[0] in VALID_VARIABLE_TYPES:
            token_type, _ = self.current_token()

            if token_type == 'INTEGERS':
                self.cpp_code.append(f"int {self.parse_variable_list()};")
            elif token_type == 'CHARACTERS':
                self.cpp_code.append(f"std::string {self.parse_variable_list()};")
            elif token_type == 'REAL':
                self.cpp_code.append(f"float {self.parse_variable_list()};")
            elif token_type == 'LOGICAL':
                self.cpp_code.append(f"bool {self.parse_variable_list()};")
            else:
                raise SyntaxError(f"Unexpected variable type '{token_type}'")

            self.next_token()  # Move to the next token after processing the type


    def parse_variable_list(self):
        variables = []
        self.next_token()  # Skip the type token (e.g., 'ΑΚΕΡΑΙΕΣ')

        # Ensure the next token is a colon
        if not self.current_token() or self.current_token()[0] != 'COLON':
            raise SyntaxError("Expected ':' after variable type")
        self.next_token()  # Skip the colon

        # Parse variable names
        while self.current_token() and self.current_token()[0] == 'IDENTIFIER':
            _, var_name = self.current_token()
            variables.append(var_name)
            self.next_token()  # Move to the next token
            if self.current_token() and self.current_token()[0] == 'COMMA':
                self.next_token()  # Skip the comma

        if not variables:
            raise SyntaxError("Expected at least one variable name")
        return ", ".join(variables)


    def parse_read(self):
        VALID_READ_WRITE_TOKENS = {'IDENTIFIER', 'COMMA'}

        self.next_token()  # Skip 'ΔΙΑΒΑΣΕ'
        read_tokens = []
        while self.current_token() and self.current_token()[0] != 'NEWLINE':
            token_type, var_name = self.current_token()
            if token_type not in VALID_READ_WRITE_TOKENS:
                raise SyntaxError(f"Unexpected token '{var_name}' in read command")
            if token_type == 'IDENTIFIER':
                # Convert Greek variable names to English
                read_tokens.append(var_name)
            self.next_token()  # Move to the next token
        self.cpp_code.append(f"std::cin >> {' >> '.join(read_tokens)};")


    def parse_write(self):
        VALID_READ_WRITE_TOKENS = {'IDENTIFIER', 'STRING', 'NUMBER', 'FLOAT', 'OP', 'GT', 'LT', 'GTE', 'LTE', 'NEQ', 'EQ'}
        END_TOKENS = {'NEWLINE', 'COMMA'}

        self.next_token()  # Skip 'ΓΡΑΨΕ'
        write_parts = []

        while self.current_token() and self.current_token()[0] != 'NEWLINE':
            # Process each part of the expression until a comma or newline is encountered
            part_tokens = self.process_expression(VALID_READ_WRITE_TOKENS, END_TOKENS)
            write_parts.append(' '.join(part_tokens))

            # If the current token is a comma, skip it and continue
            if self.current_token() and self.current_token()[0] == 'COMMA':
                self.next_token()

        # Generate the C++ write statement
        self.cpp_code.append(f"std::cout << {' << \" \" << '.join(write_parts)} << std::endl;")

    def parse_assignment(self):
        VALID_ASSIGNMENT_TOKENS = {'OP', 'NUMBER', 'FLOAT', 'STRING', 'IDENTIFIER', 'GT', 'LT', 'GTE', 'LTE', 'NEQ', 'EQ'}
        END_TOKENS = {'NEWLINE'}

        # Get the variable being assigned to
        if self.current_token_index == 0 or self.current_token(-1)[0] != 'IDENTIFIER':
            raise SyntaxError("Expected an identifier before the assignment operator '<--'")
        _, var_name = self.current_token(-1)  # The variable is the token before '<--'

        self.next_token()  # Skip '<--'
        expression_tokens = self.process_expression(VALID_ASSIGNMENT_TOKENS, END_TOKENS)

        # Generate the C++ assignment statement
        if not expression_tokens:
            raise SyntaxError(f"Missing expression on the right-hand side of assignment for '{var_name}'")
        self.cpp_code.append(f"{var_name} = {' '.join(expression_tokens)};")


    def parse_if(self):
        VALID_CONDITIONAL_TOKENS = {'IDENTIFIER', 'NUMBER', 'FLOAT', 'STRING', 'OP', 'GT', 'LT', 'GTE', 'LTE', 'NEQ', 'EQ'}
        END_TOKENS = {'THEN', 'END_IF'}

        self.next_token()  # Skip 'ΑΝ'
        condition_tokens = self.process_expression(VALID_CONDITIONAL_TOKENS, END_TOKENS)

        translated_condition = ' '.join(condition_tokens)
        self.cpp_code.append(f"if ({translated_condition}) {{")

        if self.current_token() and self.current_token()[0] == 'THEN':
            self.next_token()  # Skip 'ΤΟΤΕ'

        # Parse the body of the IF block
        self.parse_block(['END_IF', 'ELSE_IF', 'ELSE'])
        self.cpp_code.append("}")

        # Handle ΑΛΛΙΩΣ_ΑΝ (else if) recursively
        while self.current_token() and self.current_token()[0] == 'ELSE_IF':
            self.cpp_code.append("else ")
            self.parse_if()  # Recursively parse the else-if block

        # Handle ΑΛΛΙΩΣ (else)
        if self.current_token() and self.current_token()[0] == 'ELSE':
            self.next_token()  # Skip 'ΑΛΛΙΩΣ'
            self.cpp_code.append("else {")
            self.parse_block(['END_IF'])
            self.cpp_code.append("}")

        # End the IF block
        if self.current_token() and self.current_token()[0] == 'END_IF':
            self.next_token()  # Skip 'ΤΕΛΟΣ_ΑΝ'