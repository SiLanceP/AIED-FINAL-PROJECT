from django.db import migrations, models


def forwards(apps, schema_editor):
    from lessons.seed_data import seed

    seed(apps.get_model("lessons", "Level"), apps.get_model("lessons", "Exercise"))


class Migration(migrations.Migration):
    dependencies = [("lessons", "0003_three_levels_four_exercises")]

    operations = [
        migrations.AddField(
            model_name="exercise",
            name="pass_explanation",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Built-in explanation shown after the student passes this exercise.",
            ),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
