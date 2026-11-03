"""Seed content: 5 levels, each with ONE missing-line exercise.

Loaded by migration ``0002_seed_lessons`` and by ``python manage.py seed_lessons``
(which also re-syncs any edits made here).
"""

LEVELS = [
    # ------------------------------------------------------------------ 1
    {
        "number": 1,
        "title": "Printing Output",
        "topic": "print()",
        "summary": "Show text on the screen with the print() function.",
        "lesson_markdown": """
## What does `print()` do?

`print()` is a **function** that shows a value on the screen. Whatever you put
inside the parentheses `( )` is displayed, and then Python moves to a new line.

### Step by step

```python
print("Hello!")
```

1. `print` is the name of the function.
2. `( )` holds what we want to show.
3. `"Hello!"` is a **string** (text). Strings must be inside quotes - `"double"` or `'single'`.

**Output:**
```text
Hello!
```

### Printing several things

Separate values with commas. `print()` puts a space between them:

```python
print("I am", 17, "years old")
```
```text
I am 17 years old
```

### Common mistakes

| Mistake | Why it fails |
|---|---|
| `print(Hello)` | Without quotes, Python thinks `Hello` is a variable name. |
| `Print("Hi")` | Python is case-sensitive - it must be lowercase `print`. |
| `print("Hi"` | Every `(` needs a matching `)`. |
""",
        "exercise": {
            "instructions_markdown": """
Complete the welcome banner. The top and bottom borders are already written.

* **Missing line 1:** print the text `Hello, World!`
* **Missing line 2:** print the text `I am learning Python.`
""",
            "template_code": 'print("========================")\n____\n____\nprint("========================")',
            "solution_lines": ['print("Hello, World!")', 'print("I am learning Python.")'],
            "stdin_cases": [""],
            "constraints": {"must_call": ["print"]},
            "static_hints": [
                "To show text on the screen you use the print() function, and text must be wrapped in quotes.",
                "Each missing line is one print() call. Look at the border lines - your lines should have the same shape, just different text.",
                'Missing line 1 should be print( followed by the text "Hello, World!" in quotes, then a closing ). Check spelling, the comma and the "!" carefully.',
            ],
        },
    },
    # ------------------------------------------------------------------ 2
    {
        "number": 2,
        "title": "Variables and Data Types",
        "topic": "Variables",
        "summary": "Store values in named variables: strings, integers and booleans.",
        "lesson_markdown": """
## What is a variable?

A **variable** is a name that stores a value so you can use it later.
You create one with the **assignment operator** `=`.

### Step by step

```python
city = "Manila"
```

1. `city` is the **variable name** (letters, digits and `_`, cannot start with a digit).
2. `=` means *"store the value on the right into the name on the left"*.
3. `"Manila"` is the **value**.

### Basic data types

| Type | Example | Notes |
|---|---|---|
| `str` (string) | `"Ana"` | Text, always in quotes |
| `int` (integer) | `17` | Whole number, **no quotes** |
| `float` | `3.14` | Decimal number |
| `bool` (boolean) | `True` / `False` | Capital `T` / `F`, no quotes |

### Example

```python
pet = "Bantay"
legs = 4
print(pet, "has", legs, "legs")
print("Two pets have", legs * 2, "legs")
```
```text
Bantay has 4 legs
Two pets have 8 legs
```

> Watch out: `legs = "4"` is a **string**, so `legs * 2` would give `"44"`, and
> `legs + 1` would cause a `TypeError`.
""",
        "exercise": {
            "instructions_markdown": """
The program already stores the student's name. Create the two missing variables:

* **Missing line 1:** a variable named `age` that stores the **integer** `17`
* **Missing line 2:** a variable named `is_enrolled` that stores the **boolean** `True`

Expected output:
```text
Name: Ana
Age: 17
Next year, Ana will be 18
Is enrolled: True
```
""",
            "template_code": (
                "# Store the student's information in variables\n"
                'name = "Ana"\n'
                "____\n"
                "____\n"
                "\n"
                'print("Name:", name)\n'
                'print("Age:", age)\n'
                'print("Next year,", name, "will be", age + 1)\n'
                'print("Is enrolled:", is_enrolled)'
            ),
            "solution_lines": ["age = 17", "is_enrolled = True"],
            "stdin_cases": [""],
            "constraints": {"must_assign": ["age", "is_enrolled"]},
            "static_hints": [
                "A variable is created with the form name = value. Look at how the name variable is created on line 2.",
                "The variable names must be exactly age and is_enrolled. Numbers and booleans are NOT written in quotes.",
                "Missing line 1 assigns the whole number 17 to age (no quotes). Missing line 2 assigns the boolean True to is_enrolled - capital T and no quotes.",
            ],
        },
    },
    # ------------------------------------------------------------------ 3
    {
        "number": 3,
        "title": "Getting User Input",
        "topic": "input()",
        "summary": "Read values typed by the user and convert them with int().",
        "lesson_markdown": """
## Reading input with `input()`

`input()` pauses the program, waits for the user to type something, and
**returns it as a string**.

### Step by step

```python
color = input("Favorite color: ")
print("You like", color)
```

1. `input("Favorite color: ")` shows the **prompt** and waits.
2. Whatever the user types is returned **as a string**.
3. `color = ...` stores that string in a variable.

```text
Favorite color: blue
You like blue
```

### Converting text to numbers

Because `input()` always gives a string, you must convert it before doing math.
`int()` converts a string into an integer:

```python
year = int(input("Year: "))
print("Next year is", year + 1)
```

Read it from the **inside out**: first `input(...)` gets the text, then `int(...)`
turns it into a number, then `=` stores it.

| Without `int()` | With `int()` |
|---|---|
| `"2008" + 1` → `TypeError` | `2008 + 1` → `2009` |

> Tip: in this tutor, values for `input()` come from the **Input** box, one value per line.
> The prompt text inside `input("...")` is not graded.
""",
        "exercise": {
            "instructions_markdown": """
The program asks for a name and a birth year, then prints the user's age in 2026.

* **Missing line 1:** ask the user for their birth year, convert it to an **integer**,
  and store it in a variable named `birth_year`.

Sample run (Input box: `Ana` and `2008`):
```text
Hello, Ana!
You are 18 years old in 2026.
```
""",
            "template_code": (
                "# Ask for the user's name and birth year\n"
                'name = input("Enter your name: ")\n'
                "____\n"
                "\n"
                "age = 2026 - birth_year\n"
                'print("Hello, " + name + "!")\n'
                'print("You are", age, "years old in 2026.")'
            ),
            "solution_lines": ['birth_year = int(input("Enter your birth year: "))'],
            "stdin_cases": ["Ana\n2008", "Ben\n1999", "Carlo\n2015"],
            "constraints": {"must_call": ["input", "int"], "must_assign": ["birth_year"]},
            "static_hints": [
                "Look at line 2: it reads the name with input(). You need to do something similar for the birth year.",
                "input() always returns a string, but line 5 subtracts birth_year from 2026, so it must be a number. Which function turns a string into an integer?",
                "Missing line 1 should store into birth_year the result of int( input(...) ) - put the input() call inside int().",
            ],
        },
    },
    # ------------------------------------------------------------------ 4
    {
        "number": 4,
        "title": "Making Decisions",
        "topic": "Conditionals",
        "summary": "Run different code with if, elif and else.",
        "lesson_markdown": """
## Conditionals: `if`, `elif`, `else`

Conditionals let a program **choose** which code to run.

### Step by step

```python
temp = 30
if temp >= 30:
    print("Hot day!")
elif temp >= 20:
    print("Nice day.")
else:
    print("Cold day.")
```

1. `if temp >= 30:` - check a **condition**. If it is `True`, run the indented block.
2. `elif temp >= 20:` - "else if": checked **only** when the conditions above were `False`.
3. `else:` - runs when **none** of the conditions were `True`. It has no condition.
4. Every `if` / `elif` / `else` line **ends with a colon** `:`.
5. The code inside each branch is **indented** (4 spaces).

### Comparison operators

| Operator | Meaning |
|---|---|
| `==` | equal to (two `=` signs!) |
| `!=` | not equal to |
| `>` / `<` | greater / less than |
| `>=` / `<=` | greater / less than or equal |

> Order matters! Python checks from top to bottom and stops at the **first** `True` condition.
""",
        "exercise": {
            "instructions_markdown": """
Write the conditions that decide a student's remark from their score.
The indented `print()` lines are already written.

| Score | Remark |
|---|---|
| 90 and above | `Excellent!` |
| 75 to 89 | `Passed` |
| below 75 | `Failed` |

* **Missing line 1:** the `if` condition for **Excellent!**
* **Missing line 2:** the `elif` condition for **Passed**
* **Missing line 3:** the `else` line for **Failed**
""",
            "template_code": (
                'score = int(input("Enter your score: "))\n'
                "\n"
                "____\n"
                '    print("Excellent!")\n'
                "____\n"
                '    print("Passed")\n'
                "____\n"
                '    print("Failed")'
            ),
            "solution_lines": ["if score >= 90:", "elif score >= 75:", "else:"],
            "stdin_cases": ["95", "90", "89", "75", "74", "40"],
            "constraints": {"must_use": ["if"]},
            "static_hints": [
                "You need three branches: if, elif and else. Each of those lines must end with a colon.",
                "Python checks conditions from top to bottom. Start with the highest range (90 and above), then 75 and above. Use >= for 'and above'.",
                "Missing line 1 checks if score is greater than or equal to 90, missing line 2 is an elif checking greater than or equal to 75, and missing line 3 is just the word else followed by a colon.",
            ],
        },
    },
    # ------------------------------------------------------------------ 5
    {
        "number": 5,
        "title": "Repeating with Loops",
        "topic": "Loops",
        "summary": "Repeat code with for loops, range() and while loops.",
        "lesson_markdown": """
## Loops

Loops **repeat** a block of code so you don't have to write it many times.

### `for` loops with `range()`

```python
for i in range(1, 4):
    print("Round", i)
```
```text
Round 1
Round 2
Round 3
```

1. `range(1, 4)` produces the numbers **1, 2, 3** - the end number (4) is **not included**.
2. `for i in ...:` gives `i` each number one at a time.
3. The indented block runs once for each number.

### `while` loops

A `while` loop repeats **as long as** its condition is `True`:

```python
n = 1
while n <= 3:
    print(n)
    n = n + 1
print("Done")
```
```text
1
2
3
Done
```

1. Check `n <= 3`. If `True`, run the block.
2. Inside the block, **change** `n`, otherwise the loop never ends (an *infinite loop*).
3. When the condition becomes `False`, Python continues after the loop.

> Like `if`, the `for` and `while` lines end with a colon `:` and their block is indented.
""",
        "exercise": {
            "instructions_markdown": """
Complete both loops.

* **Missing line 1:** a `for` loop using `range()` so that `i` goes from **1 to 10**
  (prints the multiplication table of the number).
* **Missing line 2:** a `while` loop that keeps going **while `count` is greater than 0**
  (counts down 3, 2, 1).

Sample run (Input box: `5`):
```text
5 x 1 = 5
5 x 2 = 10
...
5 x 10 = 50
3
2
1
Liftoff!
```
""",
            "template_code": (
                "# Multiplication table using a for loop\n"
                'number = int(input("Enter a number: "))\n'
                "____\n"
                '    print(number, "x", i, "=", number * i)\n'
                "\n"
                "# Countdown using a while loop\n"
                "count = 3\n"
                "____\n"
                "    print(count)\n"
                "    count = count - 1\n"
                'print("Liftoff!")'
            ),
            "solution_lines": ["for i in range(1, 11):", "while count > 0:"],
            "stdin_cases": ["5", "7", "12"],
            "constraints": {"must_use": ["for", "while"], "must_call": ["range"]},
            "static_hints": [
                "Missing line 1 needs a for loop and missing line 2 needs a while loop. Both lines end with a colon.",
                "The loop variable must be named i because line 4 uses it. Remember range(start, stop) does NOT include the stop number.",
                "Missing line 1: for i in range(1, ...) where the stop is one more than 10. Missing line 2: while followed by the condition count is greater than 0, then a colon.",
            ],
        },
    },
]


def seed(Level, Exercise):
    """Create or update all levels/exercises. Works with real or historical models."""
    for data in LEVELS:
        ex = data["exercise"]
        level, _ = Level.objects.update_or_create(
            number=data["number"],
            defaults={
                "title": data["title"],
                "topic": data["topic"],
                "summary": data["summary"],
                "lesson_markdown": data["lesson_markdown"].strip(),
            },
        )
        Exercise.objects.update_or_create(
            level=level,
            defaults={
                "instructions_markdown": ex["instructions_markdown"].strip(),
                "template_code": ex["template_code"],
                "solution_lines": ex["solution_lines"],
                "stdin_cases": ex["stdin_cases"],
                "constraints": ex["constraints"],
                "static_hints": ex["static_hints"],
            },
        )
