from django.db import migrations


def forwards(apps, schema_editor):
    from lessons.seed_data import seed

    seed(apps.get_model("lessons", "Level"), apps.get_model("lessons", "Exercise"))


class Migration(migrations.Migration):
    dependencies = [("lessons", "0001_initial")]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
