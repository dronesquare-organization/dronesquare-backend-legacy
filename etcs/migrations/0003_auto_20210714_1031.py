# Generated by Django 3.1.10 on 2021-07-14 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('etcs', '0002_auto_20210624_1549'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nestedlayers',
            old_name='isNexting',
            new_name='isNesting',
        ),
    ]
