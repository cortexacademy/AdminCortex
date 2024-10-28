# Generated by Django 5.1 on 2024-10-28 15:41

import markdownx.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RecentUpdate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", markdownx.models.MarkdownxField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RenameField(
            model_name="userdetails",
            old_name="state",
            new_name="college_state",
        ),
        migrations.RemoveField(
            model_name="userdetails",
            name="address",
        ),
        migrations.AddField(
            model_name="chapter",
            name="imageURL",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name="exam",
            name="imageURL",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name="subject",
            name="imageURL",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name="userdetails",
            name="image_url",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name="userdetails",
            name="native_state",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="userdetails",
            name="newsletter",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="userdetails",
            name="batch_year",
            field=models.CharField(
                blank=True,
                choices=[
                    (1, "1st Proff"),
                    (2, "2nd Proff"),
                    (3, "3rd Proff - Part 1"),
                    (4, "3rd Proff - Part 2"),
                    (5, "Intern"),
                    (6, "Post Intern"),
                    (7, "Other"),
                ],
                max_length=10,
                null=True,
            ),
        ),
    ]
