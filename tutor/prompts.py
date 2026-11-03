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
    return f"""LESSON: Level {exercise.level.number} - {exercise.level.title} ({exercise.level.topic})

TASK:
{exercise.instructions_markdown}

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


def report_prompt(grade_info, level_titles):
    lines = []
    for row in grade_info["levels"]:
        lines.append(
            f"Level {row['level']} ({level_titles.get(row['level'], '')}): status={row['status']}, "
            f"hints={row['hints']}, incorrect attempts={row['wrong']}"
        )
    return f"""A student finished a 5-level beginner Python tutorial. Their results:
{chr(10).join(lines)}
Grade: {grade_info['grade']} ({grade_info['reason']})

In 3-4 short sentences: congratulate them, name the topic(s) they struggled with most
(based on hints, incorrect attempts and revealed solutions), and give one concrete practice suggestion
for each weak topic. If they made no mistakes, suggest what to learn next (e.g. lists, functions)."""
