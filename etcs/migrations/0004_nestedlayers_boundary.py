# Generated by Django 3.1.10 on 2021-07-19 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etcs', '0003_auto_20210714_1031'),
    ]

    operations = [
        migrations.AddField(
            model_name='nestedlayers',
            name='boundary',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='변환 결과 바운더리'),
        ),
    ]
