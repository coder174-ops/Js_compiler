import sys
import argparse
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from errors import JSException

def run_js(code, debug_tokens=False, debug_ast=False):
    try:
        # 1. Lexical Analysis
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()

        if debug_tokens:
            print("=== TOKENS ===")
            for token in tokens:
                print(token)
            print("==============\n")

        # 2. Parsing
        parser = Parser(tokens)
        ast = parser.parse()

        if debug_ast:
            print("=== AST ===")
            print(ast)
            print("===========\n")

        # 3. Execution
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
    except JSException as e:
        # Gracefully handle compilation and execution errors without crashing the host Python process
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Internal Engine Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    arg_parser = argparse.ArgumentParser(description="Custom JavaScript Runtime built from scratch in Python.")
    arg_parser.add_argument("file", nargs="?", help="Path to JavaScript file to execute")
    arg_parser.add_argument("-c", "--code", help="JavaScript code string to execute directly")
    arg_parser.add_argument("--tokens", action="store_true", help="Print scanned tokens")
    arg_parser.add_argument("--ast", action="store_true", help="Print Abstract Syntax Tree")
    
    args = arg_parser.parse_args()

    if args.code:
        run_js(args.code, debug_tokens=args.tokens, debug_ast=args.ast)
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                code = f.read()
            run_js(code, debug_tokens=args.tokens, debug_ast=args.ast)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Default behavior: run nested loops target code
        target_code = """
for (let i = 1; i <= 5; i++) { 
    let row = ""; 
    for (let j = 1; j <= i; j++) { 
        row += "*"; 
    } 
    console.log(row); 
}
"""
        print("No script or code provided. Executing default nested loops code:\n")
        run_js(target_code, debug_tokens=args.tokens, debug_ast=args.ast)

if __name__ == "__main__":
    main()
