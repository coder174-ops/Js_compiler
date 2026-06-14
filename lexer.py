class TokenType:
    # Keywords
    LET = "LET"
    CONST = "CONST"
    FOR = "FOR"
    FUNCTION = "FUNCTION"
    RETURN = "RETURN"
    IF = "IF"
    ELSE = "ELSE"
    SWITCH = "SWITCH"
    CASE = "CASE"
    DEFAULT = "DEFAULT"
    DO = "DO"
    WHILE = "WHILE"
    BREAK = "BREAK"
    NEW = "NEW"
    
    # Identifiers & Literals
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    
    # Operators
    ASSIGN = "="
    ADD_ASSIGN = "+="
    INC = "++"
    PLUS = "+"
    LE = "<="
    ARROW = "=>"
    SPREAD = "..."
    
    # Punctuation & Delimiters
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    SEMICOLON = ";"
    DOT = "."
    COLON = ":"
    COMMA = ","
    
    # End of File
    EOF = "EOF"


class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_      # str (from TokenType)
        self.value = value    # any (token value)
        self.line = line      # int (1-indexed line number)
        self.column = column  # int (1-indexed starting column)

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"


class Lexer:
    # Pre-defined keyword lookup table for O(1) keyword classification
    KEYWORDS = {
        "let": TokenType.LET,
        "const": TokenType.CONST,
        "for": TokenType.FOR,
        "function": TokenType.FUNCTION,
        "return": TokenType.RETURN,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "switch": TokenType.SWITCH,
        "case": TokenType.CASE,
        "default": TokenType.DEFAULT,
        "do": TokenType.DO,
        "while": TokenType.WHILE,
        "break": TokenType.BREAK,
        "new": TokenType.NEW,
    }

    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1

    def scan_tokens(self):
        source_len = len(self.source)
        while self.current < source_len:
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def peek(self):
        if self.current >= len(self.source):
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def match(self, expected):
        if self.current >= len(self.source):
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def scan_token(self):
        c = self.advance()
        
        # Fast path for whitespace
        if c == ' ' or c == '\r' or c == '\t':
            return
        if c == '\n':
            self.line += 1
            self.column = 1
            return
        
        # Punctuation & Delimiters
        if c == '(':
            self.add_token(TokenType.LPAREN)
        elif c == ')':
            self.add_token(TokenType.RPAREN)
        elif c == '{':
            self.add_token(TokenType.LBRACE)
        elif c == '}':
            self.add_token(TokenType.RBRACE)
        elif c == '[':
            self.add_token(TokenType.LBRACKET)
        elif c == ']':
            self.add_token(TokenType.RBRACKET)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == ':':
            self.add_token(TokenType.COLON)
        elif c == '.':
            # Check for spread operator '...'
            if self.peek() == '.' and self.peek_next() == '.':
                self.advance()  # consume second '.'
                self.advance()  # consume third '.'
                self.add_token(TokenType.SPREAD)
            else:
                self.add_token(TokenType.DOT)
        elif c == ',':
            self.add_token(TokenType.COMMA)
            
        # Operators
        elif c == '+':
            if self.match('+'):
                self.add_token(TokenType.INC)
            elif self.match('='):
                self.add_token(TokenType.ADD_ASSIGN)
            else:
                self.add_token(TokenType.PLUS)
        elif c == '<':
            if self.match('='):
                self.add_token(TokenType.LE)
            else:
                # Raise custom syntax error instead of crashing python host
                from errors import JSSyntaxError
                raise JSSyntaxError("Unexpected character '<'", self.line, self.start_column())
        elif c == '=':
            if self.match('>'):
                self.add_token(TokenType.ARROW)
            else:
                self.add_token(TokenType.ASSIGN)
            
        # Literals & Identifiers
        elif c == '"' or c == "'":
            self.string(c)
        elif c.isdigit():
            self.number()
        elif c.isalpha() or c == '_':
            self.identifier()
            
        else:
            from errors import JSSyntaxError
            raise JSSyntaxError(f"Unexpected character '{c}'", self.line, self.start_column())

    def add_token(self, type_, value=None):
        if value is None:
            value = self.source[self.start:self.current]
        self.tokens.append(Token(type_, value, self.line, self.start_column()))

    def start_column(self):
        return self.column - (self.current - self.start)

    def string(self, quote_char):
        value = ""
        source_len = len(self.source)
        while self.current < source_len and self.source[self.current] != quote_char:
            c = self.source[self.current]
            if c == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            value += c
            self.current += 1

        if self.current >= source_len:
            from errors import JSSyntaxError
            raise JSSyntaxError("Unterminated string literal", self.line, self.start_column())

        # Consume the closing quote
        self.current += 1
        self.column += 1
        self.add_token(TokenType.STRING, value)

    def number(self):
        # Scan integer part
        while self.current < len(self.source) and self.source[self.current].isdigit():
            self.current += 1
            self.column += 1
        
        # Scan fractional part
        if self.current < len(self.source) and self.source[self.current] == '.':
            # Check if followed by digit
            if self.current + 1 < len(self.source) and self.source[self.current + 1].isdigit():
                self.current += 2  # consume '.' and first digit
                self.column += 2
                while self.current < len(self.source) and self.source[self.current].isdigit():
                    self.current += 1
                    self.column += 1
                val = float(self.source[self.start:self.current])
                self.add_token(TokenType.NUMBER, val)
                return
                
        val = int(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, val)

    def identifier(self):
        source_len = len(self.source)
        while self.current < source_len:
            c = self.source[self.current]
            if c.isalnum() or c == '_':
                self.current += 1
                self.column += 1
            else:
                break

        text = self.source[self.start:self.current]
        type_ = self.KEYWORDS.get(text, TokenType.IDENTIFIER)
        self.add_token(type_)
