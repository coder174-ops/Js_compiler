class Node:
    """Base class for all AST nodes."""
    pass

class Program(Node):
    """Represents the entrypoint of the script, containing a list of statements."""
    def __init__(self, body):
        self.body = body  # list of Node

    def __repr__(self):
        return f"Program(body={self.body})"

class BlockStatement(Node):
    """Represents a block statement containing a list of statements, e.g., { let x = 1; }."""
    def __init__(self, body):
        self.body = body  # list of Node

    def __repr__(self):
        return f"BlockStatement(body={self.body})"

class VariableDeclaration(Node):
    """Represents a let/const declaration, e.g., let x = 5; or const y = 10;"""
    def __init__(self, name, init, is_const=False):
        self.name = name          # str (identifier name)
        self.init = init          # Node (Expression) or None
        self.is_const = is_const  # bool

    def __repr__(self):
        return f"VariableDeclaration(name={repr(self.name)}, init={self.init}, is_const={self.is_const})"

class ExpressionStatement(Node):
    """Wraps an expression so that it can be run as a statement."""
    def __init__(self, expression):
        self.expression = expression  # Node (Expression)

    def __repr__(self):
        return f"ExpressionStatement(expression={self.expression})"

class AssignmentExpression(Node):
    """Represents an assignment expression, e.g., x = 1 or x += 2."""
    def __init__(self, left, operator, right):
        self.left = left          # Node (Identifier or MemberExpression)
        self.operator = operator  # str ("=" or "+=")
        self.right = right        # Node (Expression)

    def __repr__(self):
        return f"AssignmentExpression(left={self.left}, operator={repr(self.operator)}, right={self.right})"

class UpdateExpression(Node):
    """Represents an increment/decrement expression, e.g., i++."""
    def __init__(self, argument, operator, prefix=False):
        self.argument = argument  # Node (Identifier)
        self.operator = operator  # str ("++")
        self.prefix = prefix      # bool (postfix vs prefix, default postfix)

    def __repr__(self):
        return f"UpdateExpression(argument={self.argument}, operator={repr(self.operator)}, prefix={self.prefix})"

class BinaryExpression(Node):
    """Represents a binary operation, e.g., x + y or i <= 5."""
    def __init__(self, left, operator, right):
        self.left = left      # Node (Expression)
        self.operator = operator  # str ("+" or "<=")
        self.right = right    # Node (Expression)

    def __repr__(self):
        return f"BinaryExpression(left={self.left}, operator={repr(self.operator)}, right={self.right})"

class ForStatement(Node):
    """Represents a for loop: for (init; test; update) body."""
    def __init__(self, init, test, update, body):
        self.init = init      # Node (VariableDeclaration or Expression or None)
        self.test = test      # Node (Expression or None)
        self.update = update  # Node (Expression or None)
        self.body = body      # Node (Statement)

    def __repr__(self):
        return f"ForStatement(init={self.init}, test={self.test}, update={self.update}, body={self.body})"

class MemberExpression(Node):
    """Represents a member access expression, e.g., console.log or array[0]."""
    def __init__(self, object_node, property_node, computed=False):
        self.object = object_node      # Node (Expression)
        self.property = property_node  # Node (Identifier or Expression)
        self.computed = computed      # bool (True for obj[prop], False for obj.prop)

    def __repr__(self):
        return f"MemberExpression(object={self.object}, property={self.property}, computed={self.computed})"

class CallExpression(Node):
    """Represents a function or method call expression, e.g., log(row)."""
    def __init__(self, callee, arguments):
        self.callee = callee          # Node (Expression)
        self.arguments = arguments    # list of Node (Expressions or SpreadElements)

    def __repr__(self):
        return f"CallExpression(callee={self.callee}, arguments={self.arguments})"

class Identifier(Node):
    """Represents a variable or property identifier, e.g., x."""
    def __init__(self, name):
        self.name = name  # str

    def __repr__(self):
        return f"Identifier(name={repr(self.name)})"

class Literal(Node):
    """Represents a primitive literal, e.g., 5 or "*"."""
    def __init__(self, value):
        self.value = value  # int, float, str, bool, or None

    def __repr__(self):
        return f"Literal(value={repr(self.value)})"

class ArrayLiteral(Node):
    """Represents an array literal, e.g., [1, 2, ...arr]."""
    def __init__(self, elements):
        self.elements = elements  # list of Node (Expressions or SpreadElements)

    def __repr__(self):
        return f"ArrayLiteral(elements={self.elements})"

class ObjectLiteral(Node):
    """Represents an object literal, e.g., {key: "value", ...other}."""
    def __init__(self, properties):
        self.properties = properties  # list of (str, Node) or SpreadElement

    def __repr__(self):
        return f"ObjectLiteral(properties={self.properties})"

class SpreadElement(Node):
    """Represents a spread element, e.g., ...arr."""
    def __init__(self, argument):
        self.argument = argument  # Node (Expression)

    def __repr__(self):
        return f"SpreadElement(argument={self.argument})"

class FunctionDeclaration(Node):
    """Represents a function declaration, e.g., function foo(a, ...b) {}."""
    def __init__(self, name, params, rest_param, body):
        self.name = name              # str
        self.params = params          # list of str
        self.rest_param = rest_param  # str or None
        self.body = body              # Node (BlockStatement)

    def __repr__(self):
        return f"FunctionDeclaration(name={repr(self.name)}, params={self.params}, rest_param={repr(self.rest_param)}, body={self.body})"

class FunctionExpression(Node):
    """Represents a function expression, e.g., const f = function(a) {}."""
    def __init__(self, name, params, rest_param, body):
        self.name = name              # str or None
        self.params = params          # list of str
        self.rest_param = rest_param  # str or None
        self.body = body              # Node (BlockStatement)

    def __repr__(self):
        return f"FunctionExpression(name={repr(self.name)}, params={self.params}, rest_param={repr(self.rest_param)}, body={self.body})"

class ArrowFunctionExpression(Node):
    """Represents an arrow function, e.g., (x) => x + 1 or () => {}."""
    def __init__(self, params, rest_param, body):
        self.params = params          # list of str
        self.rest_param = rest_param  # str or None
        self.body = body              # Node (BlockStatement or Expression)

    def __repr__(self):
        return f"ArrowFunctionExpression(params={self.params}, rest_param={repr(self.rest_param)}, body={self.body})"

class ReturnStatement(Node):
    """Represents a return statement, e.g., return 5;."""
    def __init__(self, argument):
        self.argument = argument      # Node (Expression) or None

    def __repr__(self):
        return f"ReturnStatement(argument={self.argument})"

# --- NEW CONTROL FLOW & GLOBALS AST NODES ---

class NewExpression(Node):
    """Represents a constructor call expression, e.g., new Date()."""
    def __init__(self, callee, arguments):
        self.callee = callee          # Node (Expression)
        self.arguments = arguments    # list of Node (Expressions)

    def __repr__(self):
        return f"NewExpression(callee={self.callee}, arguments={self.arguments})"

class IfStatement(Node):
    """Represents an if conditional, e.g., if (x) { ... } else { ... }."""
    def __init__(self, test, consequent, alternate=None):
        self.test = test              # Node (Expression)
        self.consequent = consequent  # Node (Statement)
        self.alternate = alternate    # Node (Statement or IfStatement) or None

    def __repr__(self):
        return f"IfStatement(test={self.test}, consequent={self.consequent}, alternate={self.alternate})"

class SwitchStatement(Node):
    """Represents a switch statement block."""
    def __init__(self, discriminant, cases):
        self.discriminant = discriminant  # Node (Expression)
        self.cases = cases                # list of SwitchCase

    def __repr__(self):
        return f"SwitchStatement(discriminant={self.discriminant}, cases={self.cases})"

class SwitchCase(Node):
    """Represents a case block in a switch statement."""
    def __init__(self, test, consequent):
        self.test = test              # Node (Expression) or None for default
        self.consequent = consequent  # list of Node (Statements)

    def __repr__(self):
        return f"SwitchCase(test={self.test}, consequent={self.consequent})"

class DoWhileStatement(Node):
    """Represents a do...while loop: do { body } while (test);"""
    def __init__(self, body, test):
        self.body = body  # Node (Statement)
        self.test = test  # Node (Expression)

    def __repr__(self):
        return f"DoWhileStatement(body={self.body}, test={self.test})"

class BreakStatement(Node):
    """Represents a break control statement: break;"""
    def __repr__(self):
        return "BreakStatement()"
