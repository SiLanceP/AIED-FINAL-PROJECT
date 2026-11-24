import markdown
from django.shortcuts import get_object_or_404, render
from django.utils.safestring import mark_safe

from .models import Level


def _md(text):
    return mark_safe(markdown.markdown(text, extensions=["fenced_code", "tables"]))


def home(request):
    return render(request, "home.html", {"levels": Level.objects.prefetch_related("exercises").all()})


def level_detail(request, number):
    level = get_object_or_404(Level.objects.prefetch_related("exercises"), number=number)
    exercises = list(level.exercises.all())
    numbers = list(Level.objects.values_list("number", flat=True))
    exercises_payload = [
        {
            "number": ex.number,
            "title": ex.title,
            "instructions_html": str(_md(ex.instructions_markdown)),
            "rows": ex.editor_rows(),
            "sample_stdin": (ex.stdin_cases or [""])[0],
        }
        for ex in exercises
    ]
    return render(
        request,
        "level.html",
        {
            "level": level,
            "exercises": exercises,
            "exercises_payload": exercises_payload,
            "interactive_terminal": level.number == 3,
            "lesson_html": _md(level.lesson_markdown),
            "prev_number": number - 1 if number - 1 in numbers else None,
            "next_number": number + 1 if number + 1 in numbers else None,
            "level_numbers": numbers,
        },
    )


def report(request):
    return render(request, "report.html", {"levels": Level.objects.prefetch_related("exercises").all()})
