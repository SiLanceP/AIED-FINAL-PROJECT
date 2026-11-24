from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
    from lessons.seed_data import seed

    seed(apps.get_model("lessons", "Level"), apps.get_model("lessons", "Exercise"))


class Migration(migrations.Migration):
    dependencies = [("lessons", "0002_seed_lessons")]

    operations = [
        migrations.AddField(
            model_name="exercise",
            name="number",
            field=models.PositiveIntegerField(default=1, help_text="Exercise number within the level (1..4)."),
        ),
        migrations.AddField(
            model_name="exercise",
            name="title",
            field=models.CharField(default="Exercise", max_length=100),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="level",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="exercises",
                to="lessons.level",
            ),
        ),
        migrations.AlterModelOptions(
            name="exercise",
            options={"ordering": ["level__number", "number"]},
        ),
        migrations.AddConstraint(
            model_name="exercise",
            constraint=models.UniqueConstraint(fields=("level", "number"), name="unique_level_exercise_number"),
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
