# Generated by Django 3.1.10 on 2021-07-26 11:09

from django.db import migrations, models
import projects.models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_auto_20210720_0850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anomalytypes',
            name='types',
            field=models.JSONField(default=projects.models.anomalyType_default_value, verbose_name='이슈 타입'),
        ),
    ]