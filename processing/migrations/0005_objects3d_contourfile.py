# Generated by Django 3.1.10 on 2021-08-03 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0004_auto_20210726_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='objects3d',
            name='contourFile',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='등고선 파일 경로'),
        ),
    ]
