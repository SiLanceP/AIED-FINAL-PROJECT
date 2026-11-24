from django.contrib import admin

from .models import Exercise, Level


class ExerciseInline(admin.StackedInline):
    model = Exercise
    extra = 0
    fields = (
        "number",
        "title",
        "instructions_markdown",
        "template_code",
        "solution_lines",
        "stdin_cases",
        "constraints",
        "static_hints",
    )


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "topic")
    inlines = [ExerciseInline]
