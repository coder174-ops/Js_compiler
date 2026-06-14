import sys
import math
import random
import time
import datetime
from environment import Environment
from errors import JSRuntimeError
from ast_nodes import (
    Program, BlockStatement, VariableDeclaration, ExpressionStatement,
    AssignmentExpression, UpdateExpression, BinaryExpression, ForStatement,
    MemberExpression, CallExpression, Identifier, Literal,
    ArrayLiteral, ObjectLiteral, SpreadElement,
    FunctionDeclaration, FunctionExpression, ArrowFunctionExpression, ReturnStatement,
    NewExpression, IfStatement, SwitchStatement, SwitchCase, DoWhileStatement, BreakStatement
)

class ReturnException(Exception):
    """Exception used to unwind Python stack and implement return functionality."""
    def __init__(self, value):
        super().__init__()
        self.value = value


class BreakException(Exception):
    """Exception used to unwind statement blocks and implement break functionality."""
    pass


class JSDate:
    """Represents a Date object instance in the JS runtime."""
    def __init__(self, dt=None):
        self.dt = dt or datetime.datetime.now()

    def getFullYear(self):
        return self.dt.year

    def getMonth(self):
        return self.dt.month - 1  # 0-indexed in JS

    def getDate(self):
        return self.dt.day

    def getHours(self):
        return self.dt.hour

    def __repr__(self):
        return self.dt.isoformat()


class JSDateConstructor:
    """Represents the global Date constructor function."""
    def __call__(self, *args):
        # Called as normal function Date(): returns string representation
        return datetime.datetime.now().ctime()

    def now(self):
        # Returns millisecond timestamp
        return int(time.time() * 1000)

    def construct(self, *args):
        # Instantiated via `new Date()`
        return JSDate()


# Global Math object mapping
JS_MATH = {
    "random": lambda: random.random(),
    "floor": lambda x: math.floor(x),
    "ceil": lambda x: math.ceil(x),
    "round": lambda x: math.floor(x + 0.5),
    "abs": lambda x: abs(x),
    "min": lambda *args: min(args) if args else float('inf'),
    "max": lambda *args: max(args) if args else float('-inf'),
}


class JSFunction:
    """Represents a JavaScript function with a lexical closure environment."""
    def __init__(self, interpreter, params, rest_param, body, closure, name=None):
        self.interpreter = interpreter
        self.params = params          # list of str
        self.rest_param = rest_param  # str or None
        self.body = body              # BlockStatement or Expression node
        self.closure = closure        # Environment
        self.name = name              # str or None

    def __call__(self, *args):
        # Create a new environment scope with parent closure
        call_env = Environment(parent=self.closure)
        
        # Bind regular parameters
        for i, param_name in enumerate(self.params):
            val = args[i] if i < len(args) else None
            call_env.declare(param_name, val)
            
        # Bind rest parameter
        if self.rest_param:
            rest_val = list(args[len(self.params):])
            call_env.declare(self.rest_param, rest_val)
            
        try:
            if not isinstance(self.body, BlockStatement):
                # Implicit expression return inside arrow functions
                return self.interpreter.execute(self.body, call_env)
            else:
                self.interpreter.execute(self.body, call_env)
        except ReturnException as r:
            return r.value
            
        return None

    def __repr__(self):
        name_str = f" {self.name}" if self.name else ""
        return f"[Function{name_str}]"


class Interpreter:
    def __init__(self):
        # Create global root environment
        self.global_env = Environment()
        
        # Initialize native globals
        self.global_env.declare("console", {
            "log": self.js_console_log
        })
        self.global_env.declare("Math", JS_MATH)
        self.global_env.declare("Date", JSDateConstructor())
        
        self.current_env = self.global_env

    def js_console_log(self, *args):
        formatted_args = []
        for arg in args:
            formatted_args.append(self.to_string(arg))
        print(" ".join(formatted_args))

    def to_string(self, val):
        if val is None:
            return "undefined"
        if isinstance(val, bool):
            return "true" if val else "false"
        if isinstance(val, list):
            return ",".join(self.to_string(x) for x in val)
        if isinstance(val, dict):
            return "[object Object]"
        if isinstance(val, JSFunction):
            return str(val)
        if isinstance(val, JSDate):
            return str(val)
        return str(val)

    def is_truthy(self, val):
        """JavaScript truthiness rules."""
        if val is None:
            return False
        if isinstance(val, bool):
            return val
        if isinstance(val, (int, float)):
            return val != 0
        if isinstance(val, str):
            return val != ""
        return True

    def coerce_plus(self, left_val, right_val):
        # JS + operator coercion rules
        if isinstance(left_val, str) or isinstance(right_val, str):
            return self.to_string(left_val) + self.to_string(right_val)
        if isinstance(left_val, (list, dict)) or isinstance(right_val, (list, dict)):
            return self.to_string(left_val) + self.to_string(right_val)
            
        if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
            return left_val + right_val
        raise JSRuntimeError("TypeError", f"Invalid operands for '+' operator: {type(left_val).__name__} and {type(right_val).__name__}")

    def interpret(self, program_node):
        """Execute the Program AST node directly inside the host language."""
        self.execute(program_node, self.global_env)

    def execute(self, node, env):
        if node is None:
            return None
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, env)

    def generic_visit(self, node, env):
        raise NotImplementedError(f"No visit_{type(node).__name__} method defined for class {type(node).__name__}.")

    # --- Visitor Methods ---

    def visit_Program(self, node, env):
        for stmt in node.body:
            self.execute(stmt, env)
        return None

    def visit_BlockStatement(self, node, env):
        block_env = Environment(parent=env)
        for stmt in node.body:
            self.execute(stmt, block_env)
        return None

    def visit_VariableDeclaration(self, node, env):
        value = None
        if node.init is not None:
            value = self.execute(node.init, env)
        env.declare(node.name, value, is_const=node.is_const)
        return None

    def visit_ExpressionStatement(self, node, env):
        self.execute(node.expression, env)
        return None

    def visit_AssignmentExpression(self, node, env):
        right_value = self.execute(node.right, env)
        
        if isinstance(node.left, Identifier):
            name = node.left.name
            if node.operator == "=":
                env.assign(name, right_value)
                return right_value
            elif node.operator == "+=":
                current_value = env.lookup(name)
                new_value = self.coerce_plus(current_value, right_value)
                env.assign(name, new_value)
                return new_value
                
        elif isinstance(node.left, MemberExpression):
            obj = self.execute(node.left.object, env)
            
            if node.left.computed:
                prop_name = self.execute(node.left.property, env)
            else:
                prop_name = node.left.property.name
                
            if node.operator == "=":
                if isinstance(obj, dict):
                    obj[prop_name] = right_value
                elif isinstance(obj, list):
                    idx = int(prop_name)
                    if idx >= len(obj):
                        obj.extend([None] * (idx - len(obj) + 1))
                    obj[idx] = right_value
                else:
                    raise JSRuntimeError("TypeError", f"Cannot set property '{prop_name}' of non-object")
                return right_value
                
            elif node.operator == "+=":
                if isinstance(obj, dict):
                    current_value = obj.get(prop_name)
                    new_value = self.coerce_plus(current_value, right_value)
                    obj[prop_name] = new_value
                    return new_value
                elif isinstance(obj, list):
                    idx = int(prop_name)
                    current_value = obj[idx]
                    new_value = self.coerce_plus(current_value, right_value)
                    obj[idx] = new_value
                    return new_value
                else:
                    raise JSRuntimeError("TypeError", f"Cannot set property '{prop_name}' of non-object")
                    
        raise JSRuntimeError("ReferenceError", "Invalid left-hand side in assignment")

    def visit_UpdateExpression(self, node, env):
        if not isinstance(node.argument, Identifier):
            raise JSRuntimeError("ReferenceError", "Invalid operand in update expression")
        name = node.argument.name
        current_value = env.lookup(name)
        if not isinstance(current_value, (int, float)):
            raise JSRuntimeError("TypeError", f"Update expression operand '{name}' must be numeric")
            
        if node.operator == "++":
            new_value = current_value + 1
            env.assign(name, new_value)
            return current_value if not node.prefix else new_value
        else:
            raise NotImplementedError(f"Unsupported update operator '{node.operator}'")

    def visit_BinaryExpression(self, node, env):
        left_val = self.execute(node.left, env)
        right_val = self.execute(node.right, env)
        
        if node.operator == "+":
            return self.coerce_plus(left_val, right_val)
        elif node.operator == "<=":
            if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                return left_val <= right_val
            raise JSRuntimeError("TypeError", f"Comparison '<=' only supported between numbers (got {type(left_val).__name__} and {type(right_val).__name__})")
        else:
            raise NotImplementedError(f"Unsupported binary operator '{node.operator}'")

    def visit_ForStatement(self, node, env):
        for_env = Environment(parent=env)
        if node.init is not None:
            self.execute(node.init, for_env)
        try:
            while True:
                if node.test is not None:
                    test_result = self.execute(node.test, for_env)
                    if not test_result:
                        break
                self.execute(node.body, for_env)
                if node.update is not None:
                    self.execute(node.update, for_env)
        except BreakException:
            pass
        return None

    def visit_MemberExpression(self, node, env):
        obj = self.execute(node.object, env)
        if node.computed:
            prop_name = self.execute(node.property, env)
        else:
            prop_name = node.property.name
            
        if isinstance(obj, str):
            if prop_name == "length":
                return len(obj)
            return self.resolve_string_method(obj, prop_name)
            
        if isinstance(obj, list):
            if prop_name == "length":
                return len(obj)
            try:
                idx = int(prop_name)
                if 0 <= idx < len(obj):
                    return obj[idx]
                return None
            except ValueError:
                pass
            return self.resolve_array_method(obj, prop_name)
            
        if isinstance(obj, dict):
            if prop_name in obj:
                return obj[prop_name]
            return None
            
        raise JSRuntimeError("TypeError", f"Cannot read property '{prop_name}' of {type(obj).__name__}")

    def visit_CallExpression(self, node, env):
        callee = self.execute(node.callee, env)
        
        args = []
        for arg in node.arguments:
            if isinstance(arg, SpreadElement):
                val = self.execute(arg.argument, env)
                if isinstance(val, list):
                    args.extend(val)
                elif isinstance(val, str):
                    args.extend(list(val))
                else:
                    raise JSRuntimeError("TypeError", "Spread element in call must be iterable")
            else:
                args.append(self.execute(arg, env))
                
        if callable(callee):
            return callee(*args)
        raise JSRuntimeError("TypeError", f"Callee {node.callee} is not a function")

    def visit_Identifier(self, node, env):
        return env.lookup(node.name)

    def visit_Literal(self, node, env):
        return node.value

    def visit_ArrayLiteral(self, node, env):
        res = []
        for el in node.elements:
            if isinstance(el, SpreadElement):
                val = self.execute(el.argument, env)
                if isinstance(val, list):
                    res.extend(val)
                elif isinstance(val, str):
                    res.extend(list(val))
                else:
                    raise JSRuntimeError("TypeError", "Spread element in array must be iterable")
            else:
                res.append(self.execute(el, env))
        return res

    def visit_ObjectLiteral(self, node, env):
        res = {}
        for prop in node.properties:
            if isinstance(prop, SpreadElement):
                val = self.execute(prop.argument, env)
                if isinstance(val, dict):
                    res.update(val)
                else:
                    raise JSRuntimeError("TypeError", "Spread element in object must be an object")
            else:
                key, val_node = prop
                res[key] = self.execute(val_node, env)
        return res

    def visit_FunctionDeclaration(self, node, env):
        js_fn = JSFunction(self, node.params, node.rest_param, node.body, env, name=node.name)
        env.declare(node.name, js_fn)
        return None

    def visit_FunctionExpression(self, node, env):
        return JSFunction(self, node.params, node.rest_param, node.body, env, name=node.name)

    def visit_ArrowFunctionExpression(self, node, env):
        return JSFunction(self, node.params, node.rest_param, node.body, env)

    def visit_ReturnStatement(self, node, env):
        val = self.execute(node.argument, env) if node.argument else None
        raise ReturnException(val)

    # --- NEW VISITOR METHODS FOR CONDITIONALS & LOOPS ---

    def visit_NewExpression(self, node, env):
        callee = self.execute(node.callee, env)
        args = [self.execute(arg, env) for arg in node.arguments]
        
        if hasattr(callee, "construct"):
            return callee.construct(*args)
        raise JSRuntimeError("TypeError", f"Callee is not a constructor")

    def visit_IfStatement(self, node, env):
        test_val = self.execute(node.test, env)
        if self.is_truthy(test_val):
            self.execute(node.consequent, env)
        elif node.alternate is not None:
            self.execute(node.alternate, env)
        return None

    def visit_SwitchStatement(self, node, env):
        disc_val = self.execute(node.discriminant, env)
        
        matched_idx = -1
        default_idx = -1
        
        for idx, case in enumerate(node.cases):
            if case.test is None:
                default_idx = idx
            else:
                case_val = self.execute(case.test, env)
                if case_val == disc_val:
                    matched_idx = idx
                    break
                    
        start_idx = matched_idx if matched_idx != -1 else default_idx
        if start_idx == -1:
            return None
            
        try:
            for idx in range(start_idx, len(node.cases)):
                for stmt in node.cases[idx].consequent:
                    self.execute(stmt, env)
        except BreakException:
            pass
            
        return None

    def visit_DoWhileStatement(self, node, env):
        try:
            while True:
                self.execute(node.body, env)
                test_val = self.execute(node.test, env)
                if not self.is_truthy(test_val):
                    break
        except BreakException:
            pass
        return None

    def visit_BreakStatement(self, node, env):
        raise BreakException()

    # --- Native String & Array Method Resolutions ---

    def resolve_array_method(self, array_obj, method_name):
        if method_name == "push":
            return lambda *args: (array_obj.extend(args) or len(array_obj))
            
        elif method_name == "pop":
            return lambda: array_obj.pop() if array_obj else None
            
        elif method_name == "shift":
            return lambda: array_obj.pop(0) if array_obj else None
            
        elif method_name == "unshift":
            def unshift(*args):
                for arg in reversed(args):
                    array_obj.insert(0, arg)
                return len(array_obj)
            return unshift
            
        elif method_name == "slice":
            def slice_method(start=None, end=None):
                length = len(array_obj)
                s = 0 if start is None else int(start)
                if s < 0:
                    s = max(length + s, 0)
                else:
                    s = min(s, length)
                
                e = length if end is None else int(end)
                if e < 0:
                    e = max(length + e, 0)
                else:
                    e = min(e, length)
                    
                if s >= e:
                    return []
                return array_obj[s:e]
            return slice_method
            
        elif method_name == "splice":
            def splice_method(start, delete_count=None, *items):
                length = len(array_obj)
                s = int(start)
                if s < 0:
                    s = max(length + s, 0)
                else:
                    s = min(s, length)
                    
                if delete_count is None:
                    dc = length - s
                else:
                    dc = max(int(delete_count), 0)
                    dc = min(dc, length - s)
                    
                deleted = array_obj[s:s+dc]
                array_obj[s:s+dc] = list(items)
                return deleted
            return splice_method
            
        elif method_name == "concat":
            def concat_method(*args):
                res = list(array_obj)
                for arg in args:
                    if isinstance(arg, list):
                        res.extend(arg)
                    else:
                        res.append(arg)
                return res
            return concat_method
            
        elif method_name == "includes":
            def includes_method(search_element, from_index=0):
                length = len(array_obj)
                start = int(from_index)
                if start < 0:
                    start = max(length + start, 0)
                return search_element in array_obj[start:]
            return includes_method
            
        elif method_name == "indexOf":
            def index_of_method(search_element, from_index=0):
                length = len(array_obj)
                start = int(from_index)
                if start < 0:
                    start = max(length + start, 0)
                for idx in range(start, length):
                    if array_obj[idx] == search_element:
                        return idx
                return -1
            return index_of_method
            
        elif method_name == "sort":
            def sort_method(compare_fn=None):
                if compare_fn is None:
                    array_obj.sort(key=lambda x: self.to_string(x))
                else:
                    from functools import cmp_to_key
                    def py_compare(a, b):
                        res = compare_fn(a, b)
                        if not isinstance(res, (int, float)):
                            return 0
                        return -1 if res < 0 else (1 if res > 0 else 0)
                    array_obj.sort(key=cmp_to_key(py_compare))
                return array_obj
            return sort_method
            
        elif method_name == "reverse":
            def reverse_method():
                array_obj.reverse()
                return array_obj
            return reverse_method
            
        elif method_name == "map":
            def map_method(callback):
                res = []
                for i, val in enumerate(array_obj):
                    res.append(callback(val, i, array_obj))
                return res
            return map_method
            
        elif method_name == "filter":
            def filter_method(callback):
                res = []
                for i, val in enumerate(array_obj):
                    if callback(val, i, array_obj):
                        res.append(val)
                return res
            return filter_method
            
        elif method_name == "reduce":
            def reduce_method(callback, initial_value=None):
                length = len(array_obj)
                if length == 0 and initial_value is None:
                    raise JSRuntimeError("TypeError", "Reduce of empty array with no initial value")
                if initial_value is not None:
                    acc = initial_value
                    start = 0
                else:
                    acc = array_obj[0]
                    start = 1
                for i in range(start, length):
                    acc = callback(acc, array_obj[i], i, array_obj)
                return acc
            return reduce_method
            
        elif method_name == "find":
            def find_method(callback):
                for i, val in enumerate(array_obj):
                    if callback(val, i, array_obj):
                        return val
                return None
            return find_method
            
        elif method_name == "some":
            def some_method(callback):
                for i, val in enumerate(array_obj):
                    if callback(val, i, array_obj):
                        return True
                return False
            return some_method
            
        elif method_name == "every":
            def every_method(callback):
                for i, val in enumerate(array_obj):
                    if not callback(val, i, array_obj):
                        return False
                return True
            return every_method
            
        raise JSRuntimeError("TypeError", f"Array has no method '{method_name}'")

    def resolve_string_method(self, string_obj, method_name):
        if method_name == "replace":
            return lambda pattern, replacement: string_obj.replace(str(pattern), str(replacement), 1)
            
        elif method_name == "replaceAll":
            return lambda pattern, replacement: string_obj.replace(str(pattern), str(replacement))
            
        elif method_name == "substring":
            def substring_method(start=None, end=None):
                length = len(string_obj)
                s = 0 if start is None else int(start)
                e = length if end is None else int(end)
                if s < 0: s = 0
                if e < 0: e = 0
                s = min(s, length)
                e = min(e, length)
                if s > e:
                    s, e = e, s
                return string_obj[s:e]
            return substring_method
            
        elif method_name == "slice":
            def slice_method(start=None, end=None):
                length = len(string_obj)
                s = 0 if start is None else int(start)
                if s < 0:
                    s = max(length + s, 0)
                else:
                    s = min(s, length)
                e = length if end is None else int(end)
                if e < 0:
                    e = max(length + e, 0)
                else:
                    e = min(e, length)
                if s >= e:
                    return ""
                return string_obj[s:e]
            return slice_method
            
        elif method_name == "split":
            def split_method(separator=None, limit=None):
                if separator is None:
                    return [string_obj]
                if separator == "":
                    res = list(string_obj)
                else:
                    res = string_obj.split(separator)
                if limit is not None:
                    l = max(int(limit), 0)
                    res = res[:l]
                return res
            return split_method
            
        elif method_name == "trim":
            return lambda: string_obj.strip()
            
        elif method_name == "toUpperCase":
            return lambda: string_obj.upper()
            
        elif method_name == "toLowerCase":
            return lambda: string_obj.lower()
            
        elif method_name == "includes":
            return lambda search_string, position=0: str(search_string) in string_obj[int(position):]
            
        elif method_name == "startsWith":
            return lambda search_string, position=0: string_obj.startswith(str(search_string), int(position))
            
        elif method_name == "endsWith":
            def ends_with_method(search_string, end_position=None):
                s_str = str(search_string)
                length = len(string_obj)
                e_pos = length if end_position is None else int(end_position)
                e_pos = max(min(e_pos, length), 0)
                return string_obj[:e_pos].endswith(s_str)
            return ends_with_method
            
        elif method_name == "indexOf":
            def index_of_method(search_value, from_index=0):
                s_val = str(search_value)
                length = len(string_obj)
                start = int(from_index)
                start = max(start, 0)
                if start > length:
                    return length if s_val == "" else -1
                return string_obj.find(s_val, start)
            return index_of_method
            
        raise JSRuntimeError("TypeError", f"String has no method '{method_name}'")
