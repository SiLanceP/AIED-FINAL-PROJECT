from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Level",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.PositiveIntegerField(unique=True)),
                ("title", models.CharField(max_length=100)),
                ("topic", models.CharField(help_text="Short topic label, e.g. 'print()'", max_length=100)),
                ("summary", models.CharField(max_length=255)),
                ("lesson_markdown", models.TextField(help_text="Lesson explanation (Markdown).")),
            ],
            options={"ordering": ["number"]},
        ),
        migrations.CreateModel(
            name="Exercise",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("instructions_markdown", models.TextField()),
                ("template_code", models.TextField()),
                ("solution_lines", models.JSONField(help_text="One correct answer per missing line (in order).")),
                ("stdin_cases", models.JSONField(default=list, help_text="List of test inputs. Each item is a string, one input() value per line.")),
                ("constraints", models.JSONField(blank=True, default=dict, help_text='e.g. {"must_call": ["print"], "must_use": ["for"], "must_assign": ["age"]}')),
                ("static_hints", models.JSONField(help_text="3 escalating hints used when the AI is unavailable.")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("level", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="exercise", to="lessons.level")),
            ],
        ),
    ]
