from lexer import TokenType, Token
from ast_nodes import (
    Program, BlockStatement, VariableDeclaration, ExpressionStatement,
    AssignmentExpression, UpdateExpression, BinaryExpression, ForStatement,
    MemberExpression, CallExpression, Identifier, Literal,
    ArrayLiteral, ObjectLiteral, SpreadElement,
    FunctionDeclaration, FunctionExpression, ArrowFunctionExpression, ReturnStatement,
    NewExpression, IfStatement, SwitchStatement, SwitchCase, DoWhileStatement, BreakStatement
)
from errors import JSSyntaxError


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        """Parse all tokens and return a Program AST node."""
        statements = []
        while not self.is_at_end():
            statements.append(self.parse_statement())
        return Program(statements)

    # --- Statement Parsers ---

    def parse_statement(self):
        if self.match(TokenType.FOR):
            return self.parse_for_statement()
        if self.match(TokenType.LBRACE):
            return self.parse_block_statement()
        if self.check(TokenType.LET) or self.check(TokenType.CONST):
            return self.parse_variable_declaration()
        if self.check(TokenType.FUNCTION):
            return self.parse_function_declaration()
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        if self.match(TokenType.SWITCH):
            return self.parse_switch_statement()
        if self.match(TokenType.DO):
            return self.parse_do_while_statement()
        if self.match(TokenType.BREAK):
            return self.parse_break_statement()
        return self.parse_expression_statement()

    def parse_for_statement(self):
        self.consume(TokenType.LPAREN, "Expect '(' after 'for'.")
        
        # 1. Init
        init = None
        if self.check(TokenType.LET) or self.check(TokenType.CONST):
            init = self.parse_variable_declaration_no_semi()
        elif not self.check(TokenType.SEMICOLON):
            init = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop initializer.")
        
        # 2. Test
        test = None
        if not self.check(TokenType.SEMICOLON):
            test = self.parse_expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        
        # 3. Update
        update = None
        if not self.check(TokenType.RPAREN):
            update = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expect ')' after loop update.")
        
        # 4. Body
        body = self.parse_statement()
        
        return ForStatement(init, test, update, body)

    def parse_block_statement(self):
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.parse_statement())
        self.consume(TokenType.RBRACE, "Expect '}' after block.")
        return BlockStatement(statements)

    def parse_variable_declaration_no_semi(self):
        is_const = self.match(TokenType.CONST)
        if not is_const:
            self.consume(TokenType.LET, "Expect 'let' or 'const' keyword.")
            
        name_token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        init = None
        if self.match(TokenType.ASSIGN):
            init = self.parse_expression()
        return VariableDeclaration(name_token.value, init, is_const=is_const)

    def parse_variable_declaration(self):
        decl = self.parse_variable_declaration_no_semi()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return decl

    def parse_function_declaration(self):
        self.consume(TokenType.FUNCTION, "Expect 'function' keyword.")
        name_token = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        params, rest_param = self.parse_parameters()
        self.consume(TokenType.LBRACE, "Expect '{' before function body.")
        body = self.parse_block_statement()
        return FunctionDeclaration(name_token.value, params, rest_param, body)

    def parse_return_statement(self):
        argument = None
        if not self.check(TokenType.SEMICOLON) and not self.check(TokenType.RBRACE) and not self.is_at_end():
            argument = self.parse_expression()
            
        if not (self.check(TokenType.RBRACE) or self.is_at_end()):
            self.consume(TokenType.SEMICOLON, "Expect ';' after return statement.")
        else:
            self.match(TokenType.SEMICOLON)
            
        return ReturnStatement(argument)

    def parse_if_statement(self):
        self.consume(TokenType.LPAREN, "Expect '(' after 'if'.")
        test = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expect ')' after condition.")
        consequent = self.parse_statement()
        alternate = None
        if self.match(TokenType.ELSE):
            alternate = self.parse_statement()
        return IfStatement(test, consequent, alternate)

    def parse_switch_statement(self):
        self.consume(TokenType.LPAREN, "Expect '(' after 'switch'.")
        discriminant = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expect ')' after switch value.")
        self.consume(TokenType.LBRACE, "Expect '{' before switch cases.")
        
        cases = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            cases.append(self.parse_switch_case())
            
        self.consume(TokenType.RBRACE, "Expect '}' after switch cases.")
        return SwitchStatement(discriminant, cases)

    def parse_switch_case(self):
        if self.match(TokenType.CASE):
            test = self.parse_expression()
        else:
            self.consume(TokenType.DEFAULT, "Expect 'case' or 'default'.")
            test = None
            
        self.consume(TokenType.COLON, "Expect ':' after case value.")
        
        consequent = []
        while not self.check(TokenType.CASE) and not self.check(TokenType.DEFAULT) and not self.check(TokenType.RBRACE) and not self.is_at_end():
            consequent.append(self.parse_statement())
            
        return SwitchCase(test, consequent)

    def parse_do_while_statement(self):
        body = self.parse_statement()
        self.consume(TokenType.WHILE, "Expect 'while' after 'do' body.")
        self.consume(TokenType.LPAREN, "Expect '(' after 'while'.")
        test = self.parse_expression()
        self.consume(TokenType.RPAREN, "Expect ')' after condition.")
        self.match(TokenType.SEMICOLON)  # Optional semicolon
        return DoWhileStatement(body, test)

    def parse_break_statement(self):
        if not (self.check(TokenType.RBRACE) or self.is_at_end()):
            self.match(TokenType.SEMICOLON)
        return BreakStatement()

    def parse_expression_statement(self):
        expr = self.parse_expression()
        if not (self.check(TokenType.RBRACE) or self.is_at_end()):
            self.consume(TokenType.SEMICOLON, "Expect ';' after expression statement.")
        else:
            self.match(TokenType.SEMICOLON)
        return ExpressionStatement(expr)

    # --- Parameter Parser ---

    def parse_parameters(self):
        params = []
        rest_param = None
        
        self.consume(TokenType.LPAREN, "Expect '(' before parameters.")
        if not self.check(TokenType.RPAREN):
            while True:
                if self.match(TokenType.SPREAD):
                    name = self.consume(TokenType.IDENTIFIER, "Expect parameter name after '...'").value
                    rest_param = name
                    break
                else:
                    name = self.consume(TokenType.IDENTIFIER, "Expect parameter name.").value
                    params.append(name)
                
                if not self.match(TokenType.COMMA):
                    break
                    
        self.consume(TokenType.RPAREN, "Expect ')' after parameters.")
        return params, rest_param

    # --- Expression Parsers (Precedence low to high) ---

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        expr = self.parse_comparison()
        
        if self.match(TokenType.ASSIGN, TokenType.ADD_ASSIGN):
            operator_token = self.previous()
            value = self.parse_assignment()
            
            if isinstance(expr, (Identifier, MemberExpression)):
                return AssignmentExpression(expr, operator_token.value, value)
            else:
                token = self.peek()
                raise JSSyntaxError("Invalid assignment target.", token.line, token.column)
                
        return expr

    def parse_comparison(self):
        expr = self.parse_additive()
        
        while self.match(TokenType.LE):
            operator = self.previous().value
            right = self.parse_additive()
            expr = BinaryExpression(expr, operator, right)
            
        return expr

    def parse_additive(self):
        expr = self.parse_postfix()
        
        while self.match(TokenType.PLUS):
            operator = self.previous().value
            right = self.parse_postfix()
            expr = BinaryExpression(expr, operator, right)
            
        return expr

    def parse_postfix(self):
        expr = self.parse_call_or_member()
        
        if self.match(TokenType.INC):
            operator = self.previous().value
            return UpdateExpression(expr, operator, prefix=False)
            
        return expr

    def parse_call_or_member(self):
        expr = self.parse_primary()
        
        while True:
            if self.match(TokenType.DOT):
                prop_token = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = MemberExpression(expr, Identifier(prop_token.value), computed=False)
            elif self.match(TokenType.LBRACKET):
                prop_expr = self.parse_expression()
                self.consume(TokenType.RBRACKET, "Expect ']' after computed property.")
                expr = MemberExpression(expr, prop_expr, computed=True)
            elif self.match(TokenType.LPAREN):
                arguments = []
                if not self.check(TokenType.RPAREN):
                    if self.match(TokenType.SPREAD):
                        arguments.append(SpreadElement(self.parse_expression()))
                    else:
                        arguments.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        if self.match(TokenType.SPREAD):
                            arguments.append(SpreadElement(self.parse_expression()))
                        else:
                            arguments.append(self.parse_expression())
                self.consume(TokenType.RPAREN, "Expect ')' after arguments.")
                expr = CallExpression(expr, arguments)
            else:
                break
                
        return expr

    def parse_primary(self):
        if self.match(TokenType.NEW):
            callee = self.parse_call_or_member()
            arguments = []
            if self.match(TokenType.LPAREN):
                if not self.check(TokenType.RPAREN):
                    arguments.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        arguments.append(self.parse_expression())
                self.consume(TokenType.RPAREN, "Expect ')' after arguments.")
            return NewExpression(callee, arguments)

        if self.is_arrow_function_start():
            return self.parse_arrow_function()
            
        if self.check(TokenType.FUNCTION):
            return self.parse_function_expression()
            
        if self.match(TokenType.LBRACKET):
            return self.parse_array_literal()
            
        if self.match(TokenType.LBRACE):
            return self.parse_object_literal()

        if self.match(TokenType.NUMBER):
            return Literal(self.previous().value)
            
        if self.match(TokenType.STRING):
            return Literal(self.previous().value)
            
        if self.match(TokenType.IDENTIFIER):
            return Identifier(self.previous().value)
            
        if self.match(TokenType.LPAREN):
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression.")
            return expr
            
        token = self.peek()
        raise JSSyntaxError(f"Expect expression, got '{token.value}'", token.line, token.column)

    def parse_arrow_function(self):
        params = []
        rest_param = None
        
        if self.match(TokenType.IDENTIFIER):
            params.append(self.previous().value)
        else:
            params, rest_param = self.parse_parameters()
            
        self.consume(TokenType.ARROW, "Expect '=>' after parameters.")
        
        if self.match(TokenType.LBRACE):
            body = self.parse_block_statement()
        else:
            body = self.parse_expression()
            
        return ArrowFunctionExpression(params, rest_param, body)

    def parse_function_expression(self):
        self.consume(TokenType.FUNCTION, "Expect 'function' keyword.")
        name = None
        if self.check(TokenType.IDENTIFIER):
            name = self.advance().value
        params, rest_param = self.parse_parameters()
        self.consume(TokenType.LBRACE, "Expect '{' before function body.")
        body = self.parse_block_statement()
        return FunctionExpression(name, params, rest_param, body)

    def parse_array_literal(self):
        elements = []
        if not self.check(TokenType.RBRACKET):
            if self.match(TokenType.SPREAD):
                elements.append(SpreadElement(self.parse_expression()))
            else:
                elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                if self.check(TokenType.RBRACKET):
                    break
                if self.match(TokenType.SPREAD):
                    elements.append(SpreadElement(self.parse_expression()))
                else:
                    elements.append(self.parse_expression())
        self.consume(TokenType.RBRACKET, "Expect ']' after array elements.")
        return ArrayLiteral(elements)

    def parse_object_literal(self):
        properties = []
        if not self.check(TokenType.RBRACE):
            properties.append(self.parse_object_element())
            while self.match(TokenType.COMMA):
                if self.check(TokenType.RBRACE):
                    break
                properties.append(self.parse_object_element())
        self.consume(TokenType.RBRACE, "Expect '}' after object properties.")
        return ObjectLiteral(properties)

    def parse_object_element(self):
        if self.match(TokenType.SPREAD):
            return SpreadElement(self.parse_expression())
            
        if self.match(TokenType.IDENTIFIER, TokenType.STRING, TokenType.NUMBER):
            key_token = self.previous()
            key = key_token.value
        else:
            token = self.peek()
            raise JSSyntaxError("Expect property name or spread operator in object literal.", token.line, token.column)
            
        self.consume(TokenType.COLON, "Expect ':' after property name.")
        value = self.parse_expression()
        return (key, value)

    # --- Parser Helper Methods ---

    def match(self, *types):
        for type_ in types:
            if self.check(type_):
                self.advance()
                return True
        return False

    def check(self, type_):
        if self.is_at_end():
            return False
        return self.peek().type == type_

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.current + 1]

    def previous(self):
        return self.tokens[self.current - 1]

    def consume(self, type_, message):
        if self.check(type_):
            return self.advance()
        token = self.peek()
        raise JSSyntaxError(message, token.line, token.column)

    def is_arrow_function_start(self):
        if self.check(TokenType.IDENTIFIER) and self.peek_next().type == TokenType.ARROW:
            return True
        if self.check(TokenType.LPAREN):
            depth = 0
            i = self.current
            while i < len(self.tokens):
                t = self.tokens[i]
                if t.type == TokenType.LPAREN:
                    depth += 1
                elif t.type == TokenType.RPAREN:
                    depth -= 1
                    if depth == 0:
                        if i + 1 < len(self.tokens) and self.tokens[i+1].type == TokenType.ARROW:
                            return True
                        break
                i += 1
        return False
