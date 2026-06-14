from errors import JSRuntimeError

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.bindings = {}
        self.constants = set()

    def declare(self, name, value, is_const=False):
        """Declare a variable in the current block scope."""
        if name in self.bindings:
            raise JSRuntimeError("SyntaxError", f"Identifier '{name}' has already been declared")
        self.bindings[name] = value
        if is_const:
            self.constants.add(name)

    def assign(self, name, value):
        """Assign a new value to a variable, iteratively searching the scope chain."""
        curr = self
        while curr is not None:
            if name in curr.bindings:
                if name in curr.constants:
                    raise JSRuntimeError("TypeError", f"Assignment to constant variable '{name}'")
                curr.bindings[name] = value
                return
            curr = curr.parent
        raise JSRuntimeError("ReferenceError", f"Identifier '{name}' is not defined")

    def lookup(self, name):
        """Look up the value of a variable, iteratively searching the scope chain."""
        curr = self
        while curr is not None:
            if name in curr.bindings:
                return curr.bindings[name]
            curr = curr.parent
        raise JSRuntimeError("ReferenceError", f"Identifier '{name}' is not defined")

    def __repr__(self):
        parent_repr = f"Parent<{id(self.parent)}>" if self.parent else "None"
        return f"Environment(bindings={self.bindings}, constants={self.constants}, parent={parent_repr})"
