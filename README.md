# JavaScript Runtime from Scratch in Python

A lightweight, custom JavaScript Lexer, Parser, and Tree-Walking Interpreter built entirely from scratch in Python. It parses JavaScript source code into an Abstract Syntax Tree (AST), runs evaluations under lexical scopes, supports standard library native bridges, and handles exceptions cleanly.

---

## 🚀 Key Features

*   **Variables & Scoping**: Lexical scoping for variables declared with `let` and `const` (throws type errors on constant reassignments).
*   **Complex Data Types**: Handles Array literals `[1, 2, ...arr]` and Object literals `{key: "value", ...other}`.
*   **Method Bridges**: Maps JS methods to Python implementation wrappers.
    *   *Arrays*: `push`, `pop`, `shift`, `unshift`, `slice`, `splice`, `concat`, `includes`, `indexOf`, `sort`, `reverse`, `map`, `filter`, `reduce`, `find`, `some`, `every`.
    *   *Strings*: `replace`, `replaceAll`, `substring`, `slice`, `split`, `trim`, `toUpperCase`, `toLowerCase`, `includes`, `startsWith`, `endsWith`, `indexOf`.
*   **Functions & Closures**: Supports function declarations, function expressions, arrow functions (`() => {}`), closures, and rest parameter bindings (`...args`).
*   **Control Flow**: Fully supports `if / else if / else`, `switch / case` blocks (with fallthrough and break), and `do...while` loops.
*   **Global Objects**: Pre-binds global namespaces for `Math` (rounding, bounds, bounds checks) and `Date` (construction and getters).
*   **Robust Errors**: Encapsulates errors inside `SyntaxError`, `TypeError`, and `ReferenceError` exception blocks.

---

## 🛠️ File Structure

*   `errors.py`: Implements the JavaScript-compliant exceptions hierarchy.
*   `ast_nodes.py`: Contains definitions for syntax tree nodes.
*   `lexer.py`: Character scanner converting text to tokens.
*   `environment.py`: Tracks block scoping and constant boundaries.
*   `parser.py`: Recursive descent parser parsing statements, expressions, and scopes.
*   `interpreter.py`: The evaluator that traverses the AST and executes the program.
*   `main.py`: CLI script to run raw strings or code files.
*   `test_runtime.py`: Complete test suite verifying operations.

---

## ⚡ How to Run the Project

### 1. Execute via Command Line
Run the default JS nested loop program:
```bash
python main.py
```

Run a custom JavaScript script file:
```bash
python main.py path/to/script.js
```

Run a raw JS code string directly:
```bash
python main.py -c "let x = [1, 2]; console.log(x.concat([3, 4]));"
```

View debug AST or Token outputs:
```bash
python main.py path/to/script.js --ast --tokens
```

---

### 2. Run the Test Suite
Execute the unit and integration tests:
```bash
python test_runtime.py
```

---

### 3. Run and Debug in VS Code
This project includes pre-configured launch tasks:
1. Open the project folder (`E:\js_runtime`) in VS Code.
2. Press `Ctrl + Shift + D` to open the **Run and Debug** panel.
3. Select one of the configurations:
   * **`JS Runtime: Execute Default Code`**: Runs the CLI tool.
   * **`JS Runtime: Execute Active JS File`**: Runs whatever JS file is currently open in your editor.
   * **`JS Runtime: Run Tests`**: Executes the test suite.
4. Press `F5` to run or debug!
