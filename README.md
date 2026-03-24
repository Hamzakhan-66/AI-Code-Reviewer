# AI Code Reviewer (GenAI Project)

## Overview

AI Code Reviewer is a Generative AI tool that analyzes code like a senior software engineer.

It detects bugs, suggests improvements, explains logic, and provides a clean refactored version of the code.

---

## Features

*  Bug detection (with line numbers)
*  Code improvement suggestions
*  Simple explanation of logic
*  Refactored clean code output
*  Multi-language support (Python, JavaScript, C++)
*  File input support (.py, .js, .cpp)

---

##  Tech Stack

* Python
* Groq API (LLM)
* Prompt Engineering

---

##  How It Works

1. User provides a code file or input
2. Code is sent to LLM with structured prompt
3. AI analyzes and returns:

   * Bugs
   * Improvements
   * Explanation
   * Refactored Code

---

##  Usage

### 1. Install dependencies

pip install -r requirements.txt

### 2. Add API key

Create a `.env` file:
GROQ_API_KEY=your_api_key_here

### 3. Run the script

python main.py

### 4. Input

* Enter file path
* Select programming language

---

## Example Output

1. Bugs:

* Missing colon in function definition

2. Improvements:

* Add error handling

3. Explanation:

* This function divides two numbers...

4. Refactored Code:

```python
def divide(a, b):
    if b == 0:
        return "Cannot divide by zero"
    return a / b
```

---

## Future Improvements

* Web UI (Streamlit / React)
* Drag & drop file upload
* Code editor integration
* PDF report generation

---

## Use Cases

* Developers for code review
* Students for learning
* Interview preparation

---

## Contribute

Feel free to fork and improve this project!

---
