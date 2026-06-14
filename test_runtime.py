import unittest
import io
import sys
from lexer import Lexer, TokenType
from parser import Parser
from environment import Environment
from interpreter import Interpreter
from errors import JSRuntimeError, JSSyntaxError

class TestLexer(unittest.TestCase):
    def test_lexer_all_tokens(self):
        lexer = Lexer("const let function return if else switch case default do while break new => ... [ ] :")
        tokens = lexer.scan_tokens()
        token_types = [t.type for t in tokens]
        expected = [
            TokenType.CONST, TokenType.LET, TokenType.FUNCTION, TokenType.RETURN,
            TokenType.IF, TokenType.ELSE, TokenType.SWITCH, TokenType.CASE,
            TokenType.DEFAULT, TokenType.DO, TokenType.WHILE, TokenType.BREAK,
            TokenType.NEW, TokenType.ARROW, TokenType.SPREAD, TokenType.LBRACKET,
            TokenType.RBRACKET, TokenType.COLON, TokenType.EOF
        ]
        self.assertEqual(token_types, expected)


class TestEnvironment(unittest.TestCase):
    def test_const_reassignment_error(self):
        env = Environment()
        env.declare("x", 10, is_const=True)
        with self.assertRaises(JSRuntimeError) as context:
            env.assign("x", 20)
        self.assertEqual(context.exception.name, "TypeError")

    def test_undefined_variable_lookup_error(self):
        env = Environment()
        with self.assertRaises(JSRuntimeError) as context:
            env.lookup("non_existent")
        self.assertEqual(context.exception.name, "ReferenceError")


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.interpreter = Interpreter()

    def run_code(self, source):
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        old_stdout = sys.stdout
        sys.stdout = captured = io.StringIO()
        try:
            self.interpreter.interpret(ast)
        finally:
            sys.stdout = old_stdout
            
        return captured.getvalue()

    # --- Conditionals, Switch, Loops & Breaks ---

    def test_if_else_statement(self):
        source = """
        let x = 10;
        if (x <= 5) {
            console.log("first");
        } else if (x <= 15) {
            console.log("second");
        } else {
            console.log("third");
        }
        """
        output = self.run_code(source)
        self.assertEqual(output.strip(), "second")

    def test_switch_statement_with_break(self):
        source = """
        let grade = "B";
        switch (grade) {
            case "A":
                console.log("Great");
                break;
            case "B":
                console.log("Good");
                break;
            case "C":
                console.log("OK");
                break;
            default:
                console.log("Fail");
        }
        """
        output = self.run_code(source)
        self.assertEqual(output.strip(), "Good")

    def test_switch_statement_fallthrough(self):
        source = """
        let num = 1;
        switch (num) {
            case 1:
                console.log("one");
            case 2:
                console.log("two");
                break;
            case 3:
                console.log("three");
        }
        """
        output = self.run_code(source).strip().split("\n")
        self.assertEqual(output, ["one", "two"])

    def test_do_while_loop_with_break(self):
        source = """
        let i = 1;
        do {
            if (i <= 3) {
                console.log(i);
            } else {
                break;
            }
            i++;
        } while (1 <= 10);
        """
        output = self.run_code(source).strip().split("\n")
        self.assertEqual(output, ["1", "2", "3"])

    # --- Global Objects: Math & Date ---

    def test_math_object(self):
        source = """
        console.log(Math.floor(4.9));
        console.log(Math.ceil(4.1));
        console.log(Math.round(4.5));
        console.log(Math.round(4.4));
        console.log(Math.abs(-10));
        console.log(Math.min(5, 10, 2, 8));
        console.log(Math.max(5, 10, 2, 8));
        """
        expected = ["4", "5", "5", "4", "10", "2", "10"]
        output = self.run_code(source).strip().split("\n")
        self.assertEqual(output, expected)

    def test_date_object(self):
        source = """
        let d = new Date();
        console.log(d.getFullYear() <= 3000); // dynamic check for year range
        console.log(d.getMonth() <= 11);
        console.log(d.getDate() <= 31);
        console.log(d.getHours() <= 23);
        console.log(Date.now() <= 9999999999999); // dynamic timestamp verification
        """
        expected = ["true", "true", "true", "true", "true"]
        output = self.run_code(source).strip().split("\n")
        self.assertEqual(output, expected)

    # --- Coercion, Spreads, and Array Methods (Ensuring nothing broke) ---

    def test_nested_loops_target(self):
        source = """
        for (let i = 1; i <= 5; i++) { 
            let row = ""; 
            for (let j = 1; j <= i; j++) { 
                row += "*"; 
            } 
            console.log(row); 
        }
        """
        output = self.run_code(source)
        expected = "*\n**\n***\n****\n*****\n"
        self.assertEqual(output, expected)

if __name__ == "__main__":
    unittest.main()
