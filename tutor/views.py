import json
import re

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ai.providers import AIUnavailable, chat
from lessons.models import Exercise, Level

from . import prompts
from .checker import evaluate
from .grading import compute_grade

MAX_HINTS = settings.MAX_HINTS_PER_LEVEL


def _body(request):
    try:
        data = json.loads(request.body or "{}")
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}


def _exercise(number):
    return get_object_or_404(Exercise.objects.select_related("level"), level__number=number)


def _int(v, default=0):
    try:
        return max(0, int(v))
    except (TypeError, ValueError):
        return default


def _public(result):
    """Drop internal fields before sending a checker result to the browser."""
    details = {k: v for k, v in result["details"].items() if k != "code"}
    return {**result, "details": details}


def _squash(text):
    return re.sub(r"\s+", "", text).replace("'", '"')


def _leaks_solution(text, exercise):
    """True if the AI pasted a full solution line into a hint (common with small local models)."""
    squashed = _squash(text)
    return any(len(_squash(s)) > 4 and _squash(s) in squashed for s in exercise.solution_lines)


@require_POST
def check(request, number):
    """Submit answers. The browser sends its local counters; the server decides the next tutor step."""
    exercise = _exercise(number)
    data = _body(request)
    wrong, hints = _int(data.get("wrong")), min(_int(data.get("hints")), MAX_HINTS)

    result = evaluate(exercise, data.get("answers"))
    if result["correct"]:
        action = "passed"
    elif not result["counted"]:
        action = "retry"
    elif hints >= MAX_HINTS:
        action = "reveal"  # wrong again after using every hint -> solution review
    elif wrong + 1 >= 2:
        action = "suggest_hint"  # minimal feedback for the first mistakes, then offer hints
    else:
        action = "retry"
    return JsonResponse({**_public(result), "action": action})


@require_POST
def hint(request, number):
    exercise = _exercise(number)
    data = _body(request)
    used = _int(data.get("hints"))
    if used >= MAX_HINTS:
        return JsonResponse({"error": "You have used all hints for this level."}, status=400)

    answers = data.get("answers") or []
    result = evaluate(exercise, answers)
    if result["correct"]:
        return JsonResponse({"consumed": False, "hint": "Your code is already correct - press Submit!",
                             "source": "builtin"})

    hint_number = used + 1
    source, ai_error = "ai", None
    try:
        text, _cfg = chat(data.get("ai"), prompts.SYSTEM_PROMPT,
                          prompts.hint_prompt(exercise, answers, result, hint_number))
        if _leaks_solution(text, exercise):
            raise AIUnavailable("The AI hint gave away the answer, so a built-in hint was used instead.")
    except AIUnavailable as e:
        text, source, ai_error = exercise.static_hints[hint_number - 1], "builtin", str(e)

    return JsonResponse({"consumed": True, "hint": text, "hint_number": hint_number,
                         "source": source, "ai_error": ai_error})


@require_POST
def reveal(request, number):
    exercise = _exercise(number)
    data = _body(request)
    if _int(data.get("hints")) < MAX_HINTS:
        return JsonResponse({"error": "The solution is only shown after all hints are used."}, status=400)

    answers = data.get("answers") or []
    result = evaluate(exercise, answers)
    source, ai_error = "ai", None
    try:
        text, _cfg = chat(data.get("ai"), prompts.SYSTEM_PROMPT,
                          prompts.solution_prompt(exercise, answers, result), max_tokens=500)
    except AIUnavailable as e:
        source, ai_error = "builtin", str(e)
        text = f"Your last attempt: {result['message']} {exercise.static_hints[-1]}"

    return JsonResponse({
        "explanation": text,
        "source": source,
        "ai_error": ai_error,
        "solution_lines": exercise.solution_lines,
        "solution_code": exercise.reference_code(),
    })


def _builtin_summary(info, titles):
    weak = [r for r in info["levels"] if r["status"] == "failed_revealed" or r["hints"] >= 2 or r["wrong"] >= 3]
    if not weak:
        return ("Excellent work! You handled every topic confidently. "
                "Next, try learning about lists and functions in Python.")
    topics = ", ".join(f"Level {r['level']} ({titles.get(r['level'], '')})" for r in weak)
    return (f"Well done for finishing! You found these topics harder: {topics}. "
            "Re-read those lessons, then reset your progress and try those levels again without hints.")


@require_POST
def grade(request):
    data = _body(request)
    levels_map = data.get("levels") if isinstance(data.get("levels"), dict) else {}
    titles = dict(Level.objects.values_list("number", "title"))
    info = compute_grade(levels_map, sorted(titles), MAX_HINTS)

    info["summary"], info["summary_source"] = None, None
    if info["complete"] and data.get("summarize"):
        try:
            info["summary"], _ = chat(data.get("ai"), prompts.SYSTEM_PROMPT,
                                      prompts.report_prompt(info, titles), max_tokens=400)
            info["summary_source"] = "ai"
        except AIUnavailable as e:
            info["summary"], info["summary_source"] = _builtin_summary(info, titles), "builtin"
            info["ai_error"] = str(e)
    return JsonResponse(info)
