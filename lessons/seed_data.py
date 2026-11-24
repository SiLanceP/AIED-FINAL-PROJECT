"""Seed content: 3 super-beginner levels, each with 4 missing-line exercises (12 points total).

Loaded by migration ``0003_three_levels_four_exercises`` and by ``python manage.py seed_lessons``.
"""

LEVELS = [
    # ================================================================== LEVEL 1
    {
        "number": 1,
        "title": "Printing Output",
        "topic": "print()",
        "summary": "Make Python talk! Learn how to display words, sentences, and numbers on the screen.",
        "lesson_markdown": """
## Welcome to Python! 🐍

Think of a computer program like a recipe. You write one instruction per line, and Python reads your instructions from **top to bottom**.

Your very first instruction is `print()`. It tells Python: **"Show this on the screen!"**

---

### How `print()` works (Step by Step)

Look at this single line of code:

```python
print("Hello!")
```

Let's break down every piece:
1. **`print`** — the name of the command (always all **lowercase** letters).
2. **`(` and `)`** — parentheses (round brackets). Everything you want to show goes **inside** them.
3. **`"Hello!"`** — a piece of text (programmers call text a **string**). Whenever you want Python to print words, you **must wrap them in quotation marks** `" "` so Python knows it is text.

**What appears on the screen:**
```text
Hello!
```

---

### Printing more than one line

Each `print()` command starts on its own new line:

```python
print("Line 1")
print("Line 2")
```
```text
Line 1
Line 2
```

---

### Printing numbers & combining items with a comma `,`

* **Numbers** can be printed as text inside quotes (`print("2026")`) **or** as whole numbers without quotes (`print(100)`). Putting quotes around digits makes it a **string (text)**; leaving off quotes makes it a **number (integer)**:
  ```python
  print("2026")   # prints text
  print(100)      # prints a number
  ```
* You can print **words and numbers together** in one `print()` by separating them with a **comma `,`**. Python automatically puts a space between them:
  ```python
  print("Score:", 100)
  ```
  ```text
  Score: 100
  ```

---

### Watch out for these common beginner mistakes!

| What you typed | What goes wrong | How to fix it |
|---|---|---|
| `print(Hello)` | Forgot the `" "` quotes — Python gets confused because it thinks `Hello` is a secret code name. | `print("Hello")` |
| `Print("Hello")` | Used a capital `P` — Python cares about uppercase vs. lowercase! | `print("Hello")` |
| `print("Hello"` | Forgot the closing `)` at the end. | `print("Hello")` |
""",
        "exercises": [
            {
                "number": 1,
                "title": "Say Hello!",
                "instructions_markdown": """
**(1 point)** Let's make Python say hello! The top and bottom decorative lines are already written for you.

* **Missing line 1:** Use `print()` to display the text `"Hello, Python!"`
""",
                "template_code": (
                    'print("--------------------")\n'
                    "____\n"
                    'print("--------------------")'
                ),
                "solution_lines": ['print("Hello, Python!")'],
                "stdin_cases": [""],
                "constraints": {"must_call": ["print"], "print_arg_types": ["str"]},
                "static_hints": [
                    "Use the `print()` command, and wrap the text you want to show inside quotation marks.",
                    "Look at lines 1 and 3 for an example of how `print()` is written. Your line goes in between them.",
                    "Start with `print(`, put the text from the instructions inside double quotes `\"...\"`, and close it with `)`.",
                ],
                "pass_explanation": (
                    "Great job! Putting text inside quotation marks (`\"...\"`) tells Python it is a **string** (text), "
                    "and `print()` displays it right between the top and bottom border lines."
                ),
            },
            {
                "number": 2,
                "title": "Two Lines of Text",
                "instructions_markdown": """
**(1 point)** Complete the welcome card by printing two lines of text inside the border.

* **Missing line 1:** Print `Hello, World!`
* **Missing line 2:** Print `I am coding in Python.`
""",
                "template_code": (
                    'print("========================")\n'
                    "____\n"
                    "____\n"
                    'print("========================")'
                ),
                "solution_lines": ['print("Hello, World!")', 'print("I am coding in Python.")'],
                "stdin_cases": [""],
                "constraints": {"must_call": ["print"], "print_arg_types": ["str"]},
                "static_hints": [
                    "Each missing line needs its own `print()` command with text wrapped inside quotation marks.",
                    "Missing line 1 (line 2) prints the greeting, and missing line 2 (line 3) prints the sentence about coding in Python.",
                    "Follow the pattern `print(\"...\")` on both lines: first for the Hello World greeting, then for the Python sentence.",
                ],
                "pass_explanation": (
                    "Well done! Python runs your code from **top to bottom**, one line at a time, and each `print()` "
                    "command automatically starts on its own new line."
                ),
            },
            {
                "number": 3,
                "title": "Printing a Year as Text",
                "instructions_markdown": """
**(1 point)** Display the current year as **text (a string)** inside quotation marks `" "`.

* **Missing line 1:** Use `print()` with quotes `" "` around `2026` to display `"2026"`
""",
                "template_code": (
                    'print("The current year is:")\n'
                    "____"
                ),
                "solution_lines": ['print("2026")'],
                "stdin_cases": [""],
                "constraints": {
                    "must_call": ["print"],
                    "print_arg_types": ["str"],
                    "messages": {
                        "print_arg_types": 'Remember to put quotation marks `" "` around `"2026"` inside `print()` so it is printed as text.',
                    },
                },
                "static_hints": [
                    "Use `print()` with quotation marks around the year so Python treats it as text.",
                    "Look at line 1 (`print(\"The current year is:\")`). Do the same thing on line 2, with `2026` inside the quotes.",
                    "Write `print(` followed by `2026` wrapped in double quotes `\"...\"`, then close with `)`.",
                ],
                "pass_explanation": (
                    "Nice! Wrapping `\"2026\"` in quotation marks turns those digits into a **string** (text) instead of a "
                    "math number, and `print()` shows it on the screen."
                ),
            },
            {
                "number": 4,
                "title": "Words and Numbers Together",
                "instructions_markdown": """
**(1 point)** Use a comma `,` inside `print()` to display text and a number on the **same line**.

* **Missing line 1:** Use `print()` with **two items** separated by a comma: the text `"Level:"` (in quotes) and the whole number `1` (no quotes)

Expected output:
```text
Player: Alex
Level: 1
```
""",
                "template_code": (
                    'print("Player:", "Alex")\n'
                    "____"
                ),
                "solution_lines": ['print("Level:", 1)'],
                "stdin_cases": [""],
                "constraints": {
                    "must_call": ["print"],
                    "print_arg_types": ["str", "int"],
                    "messages": {
                        "print_arg_types": 'Pass two items separated by a comma inside `print()`: the text `"Level:"` in quotes, then a comma `,`, then the whole number `1` without quotes.',
                    },
                },
                "static_hints": [
                    "Look at line 1: it puts two items inside `print()` separated by a comma `,`.",
                    'Your first item inside `print()` should be the text `"Level:"` in quotes, followed by a comma, then the number `1` without quotes.',
                    "Follow the pattern `print(\"...\", number)` — put the level label in quotes first, a comma, then the number `1`.",
                ],
                "pass_explanation": (
                    "Awesome! Separating items with a **comma `,`** inside `print()` lets you mix text (`\"Level:\"`) "
                    "and a whole number (`1`) on the same line, with Python automatically adding a space between them."
                ),
            },
        ],
    },
    # ================================================================== LEVEL 2
    {
        "number": 2,
        "title": "Variables and Data Types",
        "topic": "Variables",
        "summary": "Save information in labeled boxes called variables: text, numbers, and simple math.",
        "lesson_markdown": """
## What is a Variable? 📦

Imagine a **labeled cardboard box** where you can store one piece of information.
In Python, that box is called a **variable**.

* The **label** on the outside is the **variable name** (like `name` or `score`).
* What you put **inside** the box is the **value** (like `"Ana"` or `17`).

---

### How to create a variable (Step by Step)

You create a variable using the equals sign `=`:

```python
pet = "Bantay"
```

1. **`pet`** — the name of our box (no spaces allowed; use letters, numbers, or `_`).
2. **`=`** — means **"put the value on the right into the box on the left"**.
3. **`"Bantay"`** — the value stored inside `pet`.

Now, whenever you use `pet` inside `print(pet)`, Python opens the box and shows what's inside! Notice that variable names **never** go in quotes:

```python
pet = "Bantay"
print(pet)
```
```text
Bantay
```
*(If you wrote `print("pet")` with quotes, it would literally print the word `pet` instead of `Bantay`!)*

---

### Three Basic Types of Values (Data Types)

| Type | What it means | Example | Rule |
|---|---|---|---|
| **String (`str`)** | Text / words | `city = "Manila"` | **Always** wrap in quotes `" "` |
| **Integer (`int`)** | Whole number | `age = 17` | **No quotes!** Just the number |
| **Boolean (`bool`)** | Yes / No (`True` or `False`) | `is_enrolled = True` | **No quotes**, and capital **`T`** or **`F`** |

---

### Doing Math with Number Variables

When a variable holds a number (no quotes), Python can do math with it (`+` add, `-` subtract, `*` multiply):

```python
apples = 5
print("Original:", apples)
print("Plus two:", apples + 2)
```
```text
Original: 5
Plus two: 7
```

> **Super important:** `age = 17` is a **number**, so `age + 1` gives `18`.
> `age = "17"` (with quotes) is **text**, so `age + 1` crashes with an error because Python can't add a number to a word!
""",
        "exercises": [
            {
                "number": 1,
                "title": "Create a Text Variable",
                "instructions_markdown": """
**(1 point)** Create a variable that stores a city name so the `print()` line below can display it.

* **Missing line 1:** Create a variable named `city` and store the text `"Manila"` in it.

Expected output:
```text
Welcome to Manila
```
""",
                "template_code": (
                    "# Create the city variable below\n"
                    "____\n"
                    'print("Welcome to", city)'
                ),
                "solution_lines": ['city = "Manila"'],
                "stdin_cases": [""],
                "constraints": {"must_assign": ["city"], "assign_types": {"city": "str"}},
                "static_hints": [
                    "Create a variable by writing `variable_name = value`.",
                    "The variable name on the left of `=` must be `city` (all lowercase), and the value on the right is text inside quotes.",
                    "Follow the pattern `city = \"...\"` using the city name from the instructions.",
                ],
                "pass_explanation": (
                    "Great work! The `=` sign saved the string `\"Manila\"` inside the `city` variable, so when "
                    "`print(\"Welcome to\", city)` ran on line 3, Python looked inside `city` and printed its value."
                ),
            },
            {
                "number": 2,
                "title": "Number and Boolean Variables",
                "instructions_markdown": """
**(1 point)** The student's name is already stored in `name`. Create the other two variables:

* **Missing line 1:** Create a variable named `age` that stores the whole number `17` (no quotes!).
* **Missing line 2:** Create a variable named `is_student` that stores the boolean `True` (capital `T`, no quotes!).

Expected output:
```text
Name: Ana
Age: 17
Student: True
```
""",
                "template_code": (
                    'name = "Ana"\n'
                    "____\n"
                    "____\n"
                    "\n"
                    'print("Name:", name)\n'
                    'print("Age:", age)\n'
                    'print("Student:", is_student)'
                ),
                "solution_lines": ["age = 17", "is_student = True"],
                "stdin_cases": [""],
                "constraints": {
                    "must_assign": ["age", "is_student"],
                    "assign_types": {"age": "int", "is_student": "bool"},
                },
                "static_hints": [
                    "Look at line 1 (`name = \"Ana\"`). You will use `=` in the same way, except numbers and booleans do NOT use quotes.",
                    "Missing line 1 (line 2) sets `age` to a whole number without quotes. Missing line 2 (line 3) sets `is_student` to a boolean (`True` with a capital `T`, no quotes).",
                    "Follow `age = ____` (whole number) on line 2 and `is_student = ____` (capitalized boolean, no quotes) on line 3.",
                ],
                "pass_explanation": (
                    "Spot on! Leaving off the quotes stored `17` as a real **integer** (so you could do math with it) "
                    "and `True` (with a capital `T`) as a **boolean** yes/no value."
                ),
            },
            {
                "number": 3,
                "title": "Print a Variable's Value",
                "instructions_markdown": """
**(1 point)** Two variables (`food` and `price`) are already created for you. Now display them!

* **Missing line 1:** Use `print()` to display `"Order:"` followed by the `food` variable (separated by a comma).
* **Missing line 2:** Use `print()` to display `"Pesos:"` followed by the `price` variable (separated by a comma).

Expected output:
```text
Order: Adobo
Pesos: 120
```
""",
                "template_code": (
                    'food = "Adobo"\n'
                    "price = 120\n"
                    "\n"
                    "____\n"
                    "____"
                ),
                "solution_lines": ['print("Order:", food)', 'print("Pesos:", price)'],
                "stdin_cases": [""],
                "constraints": {"must_call": ["print"], "must_ref": ["food", "price"]},
                "static_hints": [
                    'When you want `print()` to show what is inside a variable, write the variable name WITHOUT quotes, like `print("Label:", variable_name)`.',
                    'Missing line 1 (line 4) prints the `"Order:"` label and the `food` variable. Missing line 2 (line 5) prints the `"Pesos:"` label and the `price` variable.',
                    "Follow `print(\"Order:\", ____)` on line 4 and `print(\"Pesos:\", ____)` on line 5 using the variable names `food` and `price` (no quotes around them).",
                ],
                "pass_explanation": (
                    "Nice job! Writing `food` and `price` **without quotes** told Python to open those variables and "
                    "print their stored values (`Adobo` and `120`) instead of printing the words `food` and `price`."
                ),
            },
            {
                "number": 4,
                "title": "Math with Variables",
                "instructions_markdown": """
**(1 point)** You can calculate a new variable from existing variables!

* **Missing line 1:** Create a variable named `total` that adds `burger` and `drink` together using `+`.

Expected output:
```text
Total bill: 115
```
""",
                "template_code": (
                    "burger = 85\n"
                    "drink = 30\n"
                    "____\n"
                    'print("Total bill:", total)'
                ),
                "solution_lines": ["total = burger + drink"],
                "stdin_cases": [""],
                "constraints": {
                    "must_assign": ["total"],
                    "must_ref": ["burger", "drink"],
                    "must_add": True,
                },
                "static_hints": [
                    "Create a variable named `total` using `=`, and add the two existing variables with `+`.",
                    "Put `total` on the left of `=`, and add the variable names `burger` and `drink` on the right (don't just type `115`).",
                    "Follow the pattern `total = ____ + ____` using the two variable names from lines 1 and 2.",
                ],
                "pass_explanation": (
                    "Excellent! Python read `burger` (`85`) and `drink` (`30`), added them with `+`, and saved `115` "
                    "in `total`. Using variable names means your bill stays accurate even if the prices change!"
                ),
            },
        ],
    },
    # ================================================================== LEVEL 3
    {
        "number": 3,
        "title": "Getting User Input",
        "topic": "input()",
        "summary": "Ask the user questions with input() and turn typed numbers into real integers with int().",
        "lesson_markdown": """
## Listening to the User with `input()` ⌨️

So far, our programs always printed the exact same thing. What if we want to **ask the user a question** and use what they type?

That's what `input()` does! It pauses the program, waits for the user to type a line of text, and hands that text back to you so you can save it in a variable.

---

### How `input()` works (Step by Step)

```python
name = input()
print("Hello,", name)
```

1. **`input()`** — pauses the program and waits for the user to type a value right inside the **Output** terminal below (press **Enter** after typing!).
2. **`name = ...`** — saves whatever the user typed into the variable `name`.
3. **`print("Hello,", name)`** — greets the user using the name they typed!

If the user types `Maria`, the output is:
```text
Hello, Maria
```

*(Note: You can also write a question inside the parentheses like `input("What is your name? ")`, or leave it empty `input()`. In this tutor, the prompt text inside `input()` is never graded — only what your `print()` lines output!)*

---

### Turning Input into a Number with `int()` 🔢

Here is the #1 rule about `input()`:
> **`input()` ALWAYS gives you text (a string)** — even if the user typed digits like `17`!

That means if the user types `17`, Python receives the text `"17"` (with invisible quotes). If you try to do math like `"17" + 1`, Python crashes with a `TypeError`.

To turn text digits into a real whole number (an integer), wrap it with **`int(...)`**:

```python
text = input()
age = int(text)
print("Next year:", age + 1)
```

Or even shorter, put `input()` directly inside `int()`:

```python
age = int(input())
print("Next year:", age + 1)
```

| What you wrote | If user types `17` | Can you do `age + 1`? |
|---|---|---|
| `age = input()` | `"17"` (text) | ❌ Crash (`TypeError`) |
| `age = int(input())` | `17` (number) | ✅ `18` |
""",
        "exercises": [
            {
                "number": 1,
                "title": "Read the User's Name",
                "instructions_markdown": """
**(1 point)** Ask the user for their name and store it in the variable `name`.

* **Missing line 1:** Use `input()` to read a line from the user and store it in `name`.

Sample run (when the user enters `Ana`):
```text
Hello, Ana
```
""",
                "template_code": (
                    "# Read the user's name from input\n"
                    "____\n"
                    'print("Hello,", name)'
                ),
                "solution_lines": ["name = input()"],
                "stdin_cases": ["Ana", "Marco", "Liza"],
                "constraints": {"must_call": ["input"], "must_assign": ["name"]},
                "static_hints": [
                    "Call the `input()` function and save its result into a variable named `name`.",
                    "Use the `=` sign: put the variable name on the left and the `input()` call on the right.",
                    "Follow the pattern `____ = input()` using the variable name `name`.",
                ],
                "pass_explanation": (
                    "Great job! `input()` paused the program to read whatever name the user typed, and `name = ...` "
                    "saved it so line 3 could greet any user dynamically."
                ),
            },
            {
                "number": 2,
                "title": "Read Two Inputs",
                "instructions_markdown": """
**(1 point)** When a program calls `input()` twice, it reads the **first** input first, and the **second** input second.

* **Missing line 1:** Read the user's favorite color with `input()` and store it in `color`.

Sample run (when the user enters `Ana` and `blue`):
```text
Ana likes blue
```
""",
                "template_code": (
                    "name = input()\n"
                    "____\n"
                    'print(name, "likes", color)'
                ),
                "solution_lines": ["color = input()"],
                "stdin_cases": ["Ana\nblue", "Ben\ngreen", "Cara\nred"],
                "constraints": {"must_call": ["input"], "must_assign": ["color"]},
                "static_hints": [
                    "Look at line 1 (`name = input()`). Do the same thing on line 2 for the second variable.",
                    "Store the result of `input()` into a variable named `color`.",
                    "Follow the pattern `____ = input()` using the variable name `color` on line 2.",
                ],
                "pass_explanation": (
                    "Nice! Each `input()` call waits for its own line of user input — line 1 captured `name`, "
                    "and your second `input()` captured `color` so line 3 could combine both in one sentence."
                ),
            },
            {
                "number": 3,
                "title": "Convert Text to a Number",
                "instructions_markdown": """
**(1 point)** Line 1 reads `age_text` as text using `input()`. Before line 4 can calculate `age + 1`, we need to convert `age_text` into a whole number!

* **Missing line 1:** Use `int()` to convert `age_text` into an integer and store it in a variable named `age`.

Sample run (when the user enters `17`):
```text
Next year you will be 18
```
""",
                "template_code": (
                    "age_text = input()\n"
                    "____\n"
                    "\n"
                    'print("Next year you will be", age + 1)'
                ),
                "solution_lines": ["age = int(age_text)"],
                "stdin_cases": ["17", "10", "25"],
                "constraints": {"must_call": ["int"], "must_assign": ["age"], "must_ref": ["age_text"]},
                "static_hints": [
                    "To turn a text variable into a whole number, pass it inside the `int()` function.",
                    "Create a variable named `age` using `=`, and pass `age_text` inside `int(...)`.",
                    "Follow the pattern `age = int(____)` using the text variable from line 1.",
                ],
                "pass_explanation": (
                    "Well done! Because `input()` always returns text (`\"17\"`), wrapping `age_text` inside `int()` "
                    "converted it into a real integer (`17`) so Python could safely calculate `age + 1`."
                ),
            },
            {
                "number": 4,
                "title": "Age Calculator",
                "instructions_markdown": """
**(1 point)** Put it all together! Read the user's birth year **and** convert it to an integer in a single line using `int(input())`.

* **Missing line 1:** Read the birth year using `int(input())` and store it in `birth_year`.

Sample run (when the user enters `Ana` and `2008`):
```text
Hello, Ana
In 2026 you are 18
```
""",
                "template_code": (
                    "name = input()\n"
                    "____\n"
                    "\n"
                    "age = 2026 - birth_year\n"
                    'print("Hello,", name)\n'
                    'print("In 2026 you are", age)'
                ),
                "solution_lines": ["birth_year = int(input())"],
                "stdin_cases": ["Ana\n2008", "Ben\n1999", "Carlo\n2015"],
                "constraints": {"must_call": ["input", "int"], "must_assign": ["birth_year"]},
                "static_hints": [
                    "Create a variable named `birth_year` that reads input and converts it to a whole number.",
                    "Put `input()` directly inside `int(...)` so the typed text becomes a number immediately.",
                    "Follow the pattern `____ = int(input())` using the variable name `birth_year` on line 2.",
                ],
                "pass_explanation": (
                    "Fantastic! `int(input())` works from the inside out: `input()` reads the birth year as text, "
                    "and `int(...)` immediately turns it into a number so line 4 can subtract it from `2026`."
                ),
            },
        ],
    },
]


def seed(Level, Exercise):
    """Create or update the 3 levels and their 4 exercises each (12 exercises total), removing old levels."""
    field_names = {f.name for f in Exercise._meta.get_fields()}
    if "number" not in field_names:
        # Backward compatibility when 0002_seed_lessons runs before 0003 adds Exercise.number
        return
    keep_numbers = [d["number"] for d in LEVELS]
    Level.objects.exclude(number__in=keep_numbers).delete()

    for data in LEVELS:
        level, _ = Level.objects.update_or_create(
            number=data["number"],
            defaults={
                "title": data["title"],
                "topic": data["topic"],
                "summary": data["summary"],
                "lesson_markdown": data["lesson_markdown"].strip(),
            },
        )
        ex_numbers = [ex["number"] for ex in data["exercises"]]
        Exercise.objects.filter(level=level).exclude(number__in=ex_numbers).delete()
        for ex in data["exercises"]:
            defaults = {
                "title": ex["title"],
                "instructions_markdown": ex["instructions_markdown"].strip(),
                "template_code": ex["template_code"],
                "solution_lines": ex["solution_lines"],
                "stdin_cases": ex["stdin_cases"],
                "constraints": ex["constraints"],
                "static_hints": ex["static_hints"],
            }
            if "pass_explanation" in field_names:
                defaults["pass_explanation"] = ex.get("pass_explanation", "")
            Exercise.objects.update_or_create(
                level=level,
                number=ex["number"],
                defaults=defaults,
            )
