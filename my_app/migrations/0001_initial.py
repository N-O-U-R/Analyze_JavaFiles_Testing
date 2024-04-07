# Generated by Django 5.0.3 on 2024-04-07 04:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
                ('last_analyzed', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='JavaFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('javadoc_comment_lines', models.IntegerField(default=0)),
                ('single_line_comments', models.IntegerField(default=0)),
                ('multi_line_comments', models.IntegerField(default=0)),
                ('code_lines', models.IntegerField(default=0)),
                ('total_lines', models.IntegerField(default=0)),
                ('function_count', models.IntegerField(default=0)),
                ('comment_deviation_percentage', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='java_files', to='my_app.repository')),
            ],
        ),
    ]