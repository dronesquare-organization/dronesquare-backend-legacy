# Generated by Django 3.1.10 on 2021-07-14 10:31

from django.db import migrations, models
import projects.models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20210709_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anomalytypes',
            name='types',
            field=models.JSONField(default=projects.models.anomalyType_default_value, verbose_name='이슈 타입'),
        ),
    ]
