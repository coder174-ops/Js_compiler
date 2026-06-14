🚀 JavaScript Runtime from Scratch in Python

A lightweight yet powerful **JavaScript Runtime** built completely from scratch using Python. This project implements the core components of a programming language runtime, including a **Lexer**, **Parser**, **Abstract Syntax Tree (AST)**, and a **Tree-Walking Interpreter** capable of executing JavaScript-like code.

The goal of this project is to understand how modern JavaScript engines work internally by building a simplified runtime from the ground up.

✨ Features

🧠 Variables & Lexical Scoping
- Supports `let` and `const`
- Lexical (block) scoping
- Nested scope resolution
- Constant reassignment protection
- Proper closure behavior

Example:
javascript
let x = 10;

function outer() {
    let y = 20;

    return function inner() {
        return x + y;
    };
}

const fn = outer();
console.log(fn()); // 30

📦 Arrays

Supports array literals and spread operators.

javascript
let arr = [1, 2, 3];
let merged = [...arr, 4, 5];

Supported Array Methods

- push()
- pop()
- shift()
- unshift()
- slice()
- splice()
- concat()
- includes()
- indexOf()
- sort()
- reverse()
- map()
- filter()
- reduce()
- find()
- some()
- every()

---

🏗️ Objects

Supports object literals and spread syntax.

javascript
const user = {
    name: "John",
    role: "Developer"
};

const profile = {
    ...user,
    active: true
};

⚡ Functions & Closures

Function Declarations

```javascript
function greet(name) {
    return "Hello " + name;
}
```

#### Function Expressions

```javascript
const greet = function(name) {
    return "Hello " + name;
};
```

#### Arrow Functions

```javascript
const square = x => x * x;
```

#### Rest Parameters

```javascript
function sum(...nums) {
    return nums.reduce((a, b) => a + b, 0);
}
```

---

### 🔄 Control Flow

#### If / Else

```javascript
if (score > 90) {
    console.log("Excellent");
} else {
    console.log("Keep Practicing");
}
```

#### Switch / Case

```javascript
switch(day) {
    case 1:
        console.log("Monday");
        break;

    case 2:
        console.log("Tuesday");
        break;

    default:
        console.log("Unknown");
}
```

#### Do While Loop

```javascript
let i = 0;

do {
    console.log(i);
    i++;
} while(i < 5);
```

---

### 🌎 Global Objects

#### Math

Supported methods include:

```javascript
Math.round()
Math.max()
Math.min()
```

#### Date

```javascript
const d = new Date();

d.getFullYear();
d.getMonth();
d.getDate();
```

---

### 🔤 String Methods

Supported methods:

- replace()
- replaceAll()
- substring()
- slice()
- split()
- trim()
- toUpperCase()
- toLowerCase()
- includes()
- startsWith()
- endsWith()
- indexOf()

---

### 🛡️ Error Handling

The runtime provides JavaScript-style exceptions.

#### SyntaxError

```javascript
let = 10;
```

#### ReferenceError

```javascript
console.log(x);
```

#### TypeError

```javascript
const value = 10;
value = 20;
```

---

## 📂 Project Structure

```text
js_runtime/
│
├── ast_nodes.py
├── environment.py
├── errors.py
├── interpreter.py
├── lexer.py
├── parser.py
├── main.py
├── test_runtime.py
│
└── examples/
```

### File Descriptions

| File | Description |
|--------|-------------|
| `lexer.py` | Converts source code into tokens |
| `parser.py` | Builds the Abstract Syntax Tree |
| `ast_nodes.py` | AST node definitions |
| `environment.py` | Scope and variable management |
| `interpreter.py` | AST evaluation engine |
| `errors.py` | JavaScript-style exception hierarchy |
| `main.py` | CLI entry point |
| `test_runtime.py` | Unit and integration tests |

---

## ⚙️ How It Works

```text
JavaScript Source Code
          │
          ▼
       Lexer
          │
          ▼
       Tokens
          │
          ▼
       Parser
          │
          ▼
 Abstract Syntax Tree
          │
          ▼
    Interpreter
          │
          ▼
 Program Execution
```

---

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/your-username/js-runtime-python.git

cd js-runtime-python
```

### Requirements

- Python 3.8+

No external dependencies are required.

---

## ▶️ Running the Runtime

### Execute Default Program

```bash
python main.py
```

### Execute a JavaScript File

```bash
python main.py path/to/script.js
```

### Execute Inline JavaScript

```bash
python main.py -c "let x = [1,2]; console.log(x.concat([3,4]));"
```

---

## 🔍 Debugging Options

### View Tokens

```bash
python main.py script.js --tokens
```

### View AST

```bash
python main.py script.js --ast
```

### View Tokens and AST

```bash
python main.py script.js --tokens --ast
```

---

## 🧪 Running Tests

Run the complete test suite:

```bash
python test_runtime.py
```

Example Output:

```text
===================================
Running Runtime Tests...
===================================

✓ Lexer Tests Passed
✓ Parser Tests Passed
✓ Interpreter Tests Passed

All Tests Passed ✔
```

🐞 VS Code Debugging

This project includes pre-configured VS Code launch configurations.

Available Configurations

- JS Runtime: Execute Default Code
- JS Runtime: Execute Active JS File
- JS Runtime: Run Tests

Steps

1. Open the project folder in VS Code.
2. Open the **Run and Debug** panel (`Ctrl + Shift + D`).
3. Select a configuration.
4. Press **F5**.

🎯 Learning Objectives

This project demonstrates core compiler and runtime concepts including:

- Lexical Analysis
- Tokenization
- Recursive Descent Parsing
- AST Construction
- Tree-Walking Interpretation
- Scope Resolution
- Closures
- Runtime Environments
- Error Handling Systems
- Native Function Bridges

🔮 Future Improvements

Potential enhancements include:

- Class Support
- Prototype Chain
- Async / Await
- Promises
- Modules
- For Loops
- While Loops
- Try / Catch Blocks
- JSON Support
- More Math Functions
- Additional Standard Library APIs

---

🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push changes
5. Open a Pull Request
⭐ Support

If you found this project useful:

- ⭐ Star the repository
- 🍴 Fork the project
- 🛠️ Build your own language runtime

📚 Why This Project?

Modern JavaScript engines are complex systems. This project focuses on the educational side of language implementation by rebuilding key runtime components from scratch. It provides hands-on experience with interpreters, parsers, scopes, closures, AST evaluation, and programming language design.

Built with ❤️ in Python
Understanding JavaScript by Building It Yourself
