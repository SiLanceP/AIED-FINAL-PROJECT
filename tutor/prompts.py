"""Prompts for the AI tutor (hints, solution review, final report)."""

SYSTEM_PROMPT = """You are a friendly, patient Python tutor for complete beginners.
Rules you must always follow:
- Write in simple English, at most 3 short sentences unless told otherwise.
- Talk directly to the student ("you").
- Focus only on the current exercise and the student's mistake.
- Never reveal the full correct line of code unless the request says MODE: SOLUTION.
- Do not use Markdown headings. You may use `inline code` for short code fragments."""

HINT_LEVELS = {
    1: "HINT 1 (gentle nudge): name the Python concept the student needs and what is wrong in general. "
       "Do NOT mention exact code.",
    2: "HINT 2 (point to the problem): say which missing line is wrong and why. You may show a tiny "
       "example using DIFFERENT names/values from the exercise, but not the answer.",
    3: "HINT 3 (almost there): describe in words exactly what the missing line must contain, piece by piece. "
       "You may show the pattern with a gap like `if ____ >= ____:` but NEVER the complete answer line.",
}


def _numbered(code):
    return "\n".join(f"{i:>2} | {line}" for i, line in enumerate(code.splitlines(), 1))


def describe_result(result):
    d = result.get("details", {})
    parts = [f"Checker result: {result.get('message', '')}"]
    if d.get("stdin"):
        parts.append(f"Test input (one value per line):\n{d['stdin']}")
    if "output" in d:
        parts.append(f"Student's output:\n{d['output'] or '(nothing)'}")
    if "expected" in d:
        parts.append(f"Expected output:\n{d['expected']}")
    return "\n".join(parts)


def _context(exercise, answers, result):
    blanks = "\n".join(
        f"Missing line {i + 1} (code line {ln}): {answers[i] if i < len(answers) else ''!r}"
        for i, ln in enumerate(exercise.blank_line_numbers)
    )
    solution = "\n".join(f"Missing line {i + 1}: {s}" for i, s in enumerate(exercise.solution_lines))
    constraints_note = ""
    if exercise.constraints:
        constraints_note = f"\nREQUIRED CONSTRAINTS (must be followed): {exercise.constraints}\n"
    return f"""LESSON: Level {exercise.level.number} - {exercise.level.title} ({exercise.level.topic})
EXERCISE {exercise.number}: {exercise.title}

TASK:
{exercise.instructions_markdown}
{constraints_note}
CODE TEMPLATE (____ marks a missing line):
{_numbered(exercise.template_code)}

STUDENT'S ANSWERS:
{blanks}

STUDENT'S FULL CODE:
{_numbered(result.get('details', {}).get('code') or exercise.assemble(answers))}

{describe_result(result)}

REFERENCE SOLUTION (secret - for your understanding only, other correct answers may exist):
{solution}"""


def hint_prompt(exercise, answers, result, hint_number):
    return f"""{_context(exercise, answers, result)}

MODE: HINT
{HINT_LEVELS[hint_number]}
Write the hint now."""


def solution_prompt(exercise, answers, result):
    return f"""{_context(exercise, answers, result)}

MODE: SOLUTION
The student has used all hints and is still wrong. In at most 5 short sentences:
1) explain exactly what their mistake was (refer to the missing line number),
2) explain why the correct code works.
Do not repeat the full code - it will be shown separately."""


def pass_prompt(exercise, answers, result):
    return f"""{_context(exercise, answers, result)}

MODE: PASS_EXPLANATION
The student just solved this exercise correctly! In 2-3 short, encouraging sentences for a complete beginner,
explain WHY their specific line(s) of code worked and reinforce the Python concept they just practiced."""


def report_prompt(grade_info, level_titles):
    lines = []
    for row in grade_info["levels"]:
        lines.append(
            f"Level {row['level']} ({level_titles.get(row['level'], '')}): status={row['status']}, "
            f"points={row.get('points', 0)}/{row.get('max_points', 4)}, "
            f"hints={row['hints']}/{row.get('max_hints', 12)}, "
            f"solution reveals={row.get('reveals', 0)}, incorrect attempts={row['wrong']}"
        )
    return f"""A student finished a 3-level beginner Python tutorial (12 points total, 4 exercises per level, 3 hints per exercise = 36 hints max). Their results:
{chr(10).join(lines)}
Total Score: {grade_info.get('total_points', 0)} / {grade_info.get('max_points', 12)} points
Total Hints: {grade_info.get('total_hints', 0)} / {grade_info.get('max_total_hints', 36)}
Total Solution Reveals: {grade_info.get('total_reveals', 0)} / {grade_info.get('max_points', 12)}
Grade: {grade_info['grade']} ({grade_info['reason']})

In 3-4 short sentences: congratulate them, name the topic(s) they struggled with most
(based on hints, incorrect attempts and revealed solutions), and give one concrete practice suggestion
for each weak topic. If they made no mistakes, suggest what to learn next (e.g. conditionals, loops)."""
