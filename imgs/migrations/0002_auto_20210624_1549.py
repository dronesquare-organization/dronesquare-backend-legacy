# Generated by Django 3.1.10 on 2021-06-24 15:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
        ('imgs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='imgs',
            name='email',
            field=models.ForeignKey(db_column='email', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='email', verbose_name='이메일'),
        ),
        migrations.AddField(
            model_name='imgs',
            name='projectId',
            field=models.ForeignKey(db_column='projectId', on_delete=django.db.models.deletion.CASCADE, related_name='imgs', to='projects.projects', verbose_name='프로젝트 아이디'),
        ),
        migrations.AlterUniqueTogether(
            name='imgs',
            unique_together={('projectId', 'id', 'name', 'format')},
        ),
    ]
