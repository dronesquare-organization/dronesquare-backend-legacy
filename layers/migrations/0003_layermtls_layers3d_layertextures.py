# Generated by Django 3.1.10 on 2021-10-07 09:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0008_fastmosaics'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0019_auto_20211007_0944'),
        ('layers', '0002_auto_20210624_1549'),
    ]

    operations = [
        migrations.CreateModel(
            name='Layers3D',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='3d 레이어 아이디')),
                ('fileDir', models.CharField(blank=True, max_length=500, null=True, verbose_name='mtl 파일 경로')),
                ('size', models.BigIntegerField(default=0, verbose_name='파일 사이즈')),
                ('ObjId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='layer3d', to='processing.objects3d', verbose_name='3D 오브젝트 아이디')),
                ('email', models.ForeignKey(db_column='email', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='email', verbose_name='이메일')),
                ('projectId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.projects', verbose_name='프로젝트 아이디')),
            ],
            options={
                'verbose_name': '3d 레이어 정보',
                'verbose_name_plural': '3d 레이어 정보들',
                'db_table': 'layers3d',
            },
        ),
        migrations.CreateModel(
            name='LayerTextures',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='3d texture 파일 아이디')),
                ('fileDir', models.CharField(blank=True, max_length=500, null=True, verbose_name='texture 파일 경로')),
                ('size', models.BigIntegerField(default=0, verbose_name='파일 사이즈')),
                ('email', models.ForeignKey(db_column='email', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='email', verbose_name='이메일')),
                ('layerId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='layertexture', to='layers.layers3d', verbose_name='3D 레이어 아이디')),
                ('projectId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.projects', verbose_name='프로젝트 아이디')),
            ],
            options={
                'verbose_name': 'layer texture 파일',
                'verbose_name_plural': 'layer texture 파일',
                'db_table': 'layer_texture',
            },
        ),
        migrations.CreateModel(
            name='LayerMtls',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='3d mtl 파일 아이디')),
                ('fileDir', models.CharField(blank=True, max_length=500, null=True, verbose_name='mtl 파일 경로')),
                ('size', models.BigIntegerField(default=0, verbose_name='파일 사이즈')),
                ('email', models.ForeignKey(db_column='email', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='email', verbose_name='이메일')),
                ('layerId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='layermtl', to='layers.layers3d', verbose_name='3D 레이어 아이디')),
                ('projectId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.projects', verbose_name='프로젝트 아이디')),
            ],
            options={
                'verbose_name': 'layer mtl 파일',
                'verbose_name_plural': 'layer mtl 파일',
                'db_table': 'layer_mtl',
            },
        ),
    ]
