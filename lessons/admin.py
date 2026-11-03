from django.contrib import admin

from .models import Exercise, Level


class ExerciseInline(admin.StackedInline):
    model = Exercise
    extra = 0


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "topic")
    inlines = [ExerciseInline]
