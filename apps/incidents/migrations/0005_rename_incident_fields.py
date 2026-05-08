from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("incidents", "0004_alter_accident_cercle_alter_accident_commune_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="accident",
            old_name="incident_date",
            new_name="accident_date",
        ),
        migrations.RenameField(
            model_name="accident",
            old_name="incident_time",
            new_name="accident_time",
        ),
    ]