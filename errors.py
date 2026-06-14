class JSException(Exception):
    """Base class for all JavaScript-style exceptions."""
    def __init__(self, name, message):
        super().__init__(f"{name}: {message}")
        self.name = name
        self.message = message


class JSSyntaxError(JSException):
    """Represents a compilation/parsing error in JavaScript."""
    def __init__(self, message, line, column):
        super().__init__("SyntaxError", f"{message} (at line {line}, col {column})")
        self.line = line
        self.column = column


class JSRuntimeError(JSException):
    """Represents a runtime execution error (e.g. TypeError, ReferenceError)."""
    def __init__(self, name, message):
        super().__init__(name, message)
