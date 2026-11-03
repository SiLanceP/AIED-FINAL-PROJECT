import markdown
from django.shortcuts import get_object_or_404, render
from django.utils.safestring import mark_safe

from .models import Level


def _md(text):
    return mark_safe(markdown.markdown(text, extensions=["fenced_code", "tables"]))


def home(request):
    return render(request, "home.html", {"levels": Level.objects.all()})


def level_detail(request, number):
    level = get_object_or_404(Level.objects.select_related("exercise"), number=number)
    exercise = level.exercise
    numbers = list(Level.objects.values_list("number", flat=True))
    return render(
        request,
        "level.html",
        {
            "level": level,
            "exercise": exercise,
            "lesson_html": _md(level.lesson_markdown),
            "instructions_html": _md(exercise.instructions_markdown),
            "rows": exercise.editor_rows(),
            "sample_stdin": (exercise.stdin_cases or [""])[0],
            "prev_number": number - 1 if number - 1 in numbers else None,
            "next_number": number + 1 if number + 1 in numbers else None,
            "level_numbers": numbers,
        },
    )


def report(request):
    return render(request, "report.html", {"levels": Level.objects.all()})
