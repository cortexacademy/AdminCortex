# Generated by Django 5.1 on 2024-08-31 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_year_remove_attempt_option_remove_attempt_question_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studymaterial',
            name='reference',
        ),
        migrations.AddField(
            model_name='chapter',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='exam',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='question',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='subject',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='topic',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.RemoveField(
            model_name='question',
            name='chapter',
        ),
        migrations.RemoveField(
            model_name='question',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='question',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='studymaterial',
            name='topic',
        ),
        migrations.AlterField(
            model_name='year',
            name='year',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.DeleteModel(
            name='ReferenceStudyMaterial',
        ),
        migrations.AddField(
            model_name='question',
            name='chapter',
            field=models.ManyToManyField(related_name='questions', to='api.chapter'),
        ),
        migrations.AddField(
            model_name='question',
            name='subject',
            field=models.ManyToManyField(related_name='questions', to='api.subject'),
        ),
        migrations.AddField(
            model_name='question',
            name='topic',
            field=models.ManyToManyField(related_name='questions', to='api.topic'),
        ),
        migrations.AddField(
            model_name='studymaterial',
            name='topic',
            field=models.ManyToManyField(related_name='study_materials', to='api.topic'),
        ),
    ]
