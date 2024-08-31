# Generated by Django 5.1 on 2024-08-31 05:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Year',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=4, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='attempt',
            name='option',
        ),
        migrations.RemoveField(
            model_name='attempt',
            name='question',
        ),
        migrations.RemoveField(
            model_name='chapter',
            name='subject',
        ),
        migrations.RemoveField(
            model_name='question',
            name='year',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='exam',
        ),
        migrations.AddField(
            model_name='attempt',
            name='options',
            field=models.ManyToManyField(related_name='attempts', to='api.option'),
        ),
        migrations.AddField(
            model_name='attempt',
            name='questions',
            field=models.ManyToManyField(related_name='attempts', to='api.question'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='subjects',
            field=models.ManyToManyField(related_name='chapters', to='api.subject'),
        ),
        migrations.AddField(
            model_name='exam',
            name='subjects',
            field=models.ManyToManyField(related_name='exams', to='api.subject'),
        ),
        migrations.AlterField(
            model_name='attempt',
            name='user',
            field=models.UUIDField(editable=False),
        ),
        migrations.AlterField(
            model_name='solution',
            name='question',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='solution', to='api.question'),
        ),
        migrations.AddField(
            model_name='question',
            name='years',
            field=models.ManyToManyField(related_name='questions', to='api.year'),
        ),
    ]