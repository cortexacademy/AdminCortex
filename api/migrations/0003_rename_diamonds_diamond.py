# Generated by Django 5.1 on 2024-09-16 19:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_studymaterial_is_active"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Diamonds",
            new_name="Diamond",
        ),
    ]
