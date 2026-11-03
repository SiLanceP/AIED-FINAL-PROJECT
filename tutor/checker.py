"""Constraint-based checker.

A submission is correct when:
  1. every missing line is filled in,
  2. the code is valid Python,
  3. it passes the safety rules,
  4. it satisfies the exercise constraints (checked on the STUDENT'S lines only), and
  5. for every test input, its print() output matches the reference solution's output.

Because correctness is judged by output + constraints (not exact text), different
valid answers are accepted - e.g. ``range(1, 11)`` and ``range(1, 10 + 1)``.
"""

import ast

from .runner import CodeTimeout, run_cases

FORBIDDEN_CALLS = {
    "eval", "exec", "open", "compile", "__import__", "globals", "locals", "vars",
    "getattr", "setattr", "delattr", "breakpoint", "help", "memoryview", "exit", "quit",
}

USE_NODES = {"for": ast.For, "while": ast.While, "if": ast.If}
USE_LABELS = {"for": "a `for` loop", "while": "a `while` loop", "if": "an `if` statement"}

_reference_cache = {}


def _result(correct, kind, message, counted=True, **details):
    return {"correct": correct, "counted": counted, "kind": kind, "message": message, "details": details}


def _line_label(exercise, lineno):
    if lineno in exercise.blank_line_numbers:
        return f"Line {lineno} (missing line {exercise.blank_line_numbers.index(lineno) + 1})"
    return f"Line {lineno}" if lineno else "Your code"


def _normalize(text):
    lines = [ln.rstrip() for ln in (text or "").replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def safety_problem(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return node.lineno, "Imports are not needed (or allowed) in these exercises."
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            return node.lineno, f"The `{node.func.id}()` function is not allowed in these exercises."
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return node.lineno, "Special double-underscore attributes are not allowed in these exercises."
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            return node.lineno, "Special double-underscore names are not allowed in these exercises."
    return None


def constraint_problems(tree, constraints, student_lines):
    """Check constraints using only AST nodes that start on the student's lines."""
    nodes = [n for n in ast.walk(tree) if getattr(n, "lineno", None) in student_lines]
    calls = {n.func.id for n in nodes if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assigned = set()
    for n in nodes:
        targets = n.targets if isinstance(n, ast.Assign) else [getattr(n, "target", None)]
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            assigned |= {t.id for t in targets if isinstance(t, ast.Name)}

    custom = constraints.get("messages", {})
    problems = []
    for kw in constraints.get("must_use", []):
        if not any(isinstance(n, USE_NODES[kw]) for n in nodes):
            problems.append(custom.get(f"must_use:{kw}", f"Your code should use {USE_LABELS[kw]}."))
    for name in constraints.get("must_call", []):
        if name not in calls:
            problems.append(custom.get(f"must_call:{name}", f"Your code should use the `{name}()` function."))
    for name in constraints.get("must_assign", []):
        if name not in assigned:
            problems.append(custom.get(f"must_assign:{name}", f"Your code should create a variable named `{name}`."))
    return problems


def reference_outputs(exercise):
    key = (exercise.pk, exercise.updated_at)
    if key not in _reference_cache:
        _reference_cache[key] = [r["output"] for r in run_cases(exercise.reference_code(), exercise.stdin_cases)]
    return _reference_cache[key]


def evaluate(exercise, answers):
    """Grade a submission. ``answers`` = list of strings, one per missing line."""
    answers = [str(a or "").replace("\r", "").split("\n")[0] for a in (answers or [])]
    answers += [""] * (exercise.blank_count - len(answers))
    answers = answers[: exercise.blank_count]

    empty = [i + 1 for i, a in enumerate(answers) if not a.strip()]
    if empty:
        names = ", ".join(str(i) for i in empty)
        return _result(False, "incomplete", f"Fill in every missing line first (missing line {names}).", counted=False)

    code = exercise.assemble(answers)
    student_lines = set(exercise.blank_line_numbers)

    try:
        tree = ast.parse(code, filename="main.py")
    except SyntaxError as e:
        return _result(False, "syntax", f"{_line_label(exercise, e.lineno)} has a syntax error: {e.msg}.",
                       error_line=e.lineno, code=code)

    problem = safety_problem(tree)
    if problem:
        return _result(False, "forbidden", f"{_line_label(exercise, problem[0])}: {problem[1]}",
                       error_line=problem[0], code=code)

    problems = constraint_problems(tree, exercise.constraints or {}, student_lines)
    if problems:
        return _result(False, "constraint", " ".join(problems), problems=problems, code=code)

    try:
        results = run_cases(code, exercise.stdin_cases)
        expected = reference_outputs(exercise)
    except CodeTimeout:
        return _result(False, "timeout", "Your program took too long to finish. Is there a loop that never ends?",
                       code=code)

    for case, res, exp in zip(exercise.stdin_cases, results, expected):
        if res["error"]:
            return _result(False, "runtime",
                           f"{_line_label(exercise, res['error_line'])} caused an error: {res['error']}",
                           stdin=case, output=res["output"], error=res["error"],
                           error_line=res["error_line"], code=code)
        if _normalize(res["output"]) != _normalize(exp):
            return _result(False, "output", "Your program runs, but its output is not correct.",
                           stdin=case, output=res["output"], expected=exp, code=code)

    return _result(True, "correct", "Correct! Your program works for every test input.", code=code)
