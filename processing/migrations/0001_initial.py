# Generated by Django 3.1.10 on 2021-06-24 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mosaics',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='모자익 아이디')),
                ('layerName', models.CharField(max_length=200, verbose_name='모자익 레이어 이름')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='모자익 생성 일자')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='모자익 수정 일자')),
                ('volume', models.BigIntegerField(default=0, verbose_name='프로젝트 이미지 용량')),
                ('wmsURL', models.CharField(max_length=1000, verbose_name='이미지 모자익 WMS 경로')),
                ('mosaicDir', models.CharField(max_length=500, verbose_name='이미지 모자익 파일 경로')),
                ('dsmDir', models.CharField(max_length=500, verbose_name='dsm 모자익 파일 경로')),
                ('coordSystem', models.CharField(max_length=50, verbose_name='좌표계 정보')),
                ('mosaicSize', models.BigIntegerField(default=0, verbose_name='모자익 파일 사이즈')),
                ('dsmSize', models.BigIntegerField(default=0, verbose_name='dsm 파일 사이즈')),
                ('bounds', models.JSONField(default=list, verbose_name='모자익 영상 boundary')),
                ('gsd', models.FloatField(default=0, verbose_name='gsd')),
                ('voxelDir', models.CharField(blank=True, max_length=400, null=True, verbose_name='복셀 파일 경로')),
            ],
            options={
                'verbose_name': '모자익',
                'verbose_name_plural': '모자익',
                'db_table': 'mosaic',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Mtls',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='3d mtl 파일 아이디')),
                ('fileDir', models.CharField(blank=True, max_length=500, null=True, verbose_name='mtl 파일 경로')),
                ('size', models.BigIntegerField(default=0, verbose_name='파일 사이즈')),
            ],
            options={
                'verbose_name': 'mtl 파일',
                'verbose_name_plural': 'mtl 파일',
                'db_table': 'mtl',
            },
        ),
        migrations.CreateModel(
            name='Objects3D',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='3d 오브젝트 아이디')),
                ('pcdFile', models.CharField(blank=True, max_length=500, null=True, verbose_name='Point Cloud 파일 경로')),
                ('meshFile', models.CharField(blank=True, max_length=500, null=True, verbose_name='메쉬 파일 경로')),
                ('pcdSize', models.BigIntegerField(default=0, verbose_name='Point Cloud 파일 사이즈')),
                ('meshSize', models.BigIntegerField(default=0, verbose_name='메쉬 파일 사이즈')),
            ],
            options={
                'verbose_name': '3d 데이터',
                'verbose_name_plural': '3d 데이터',
                'db_table': 'object3d',
            },
        ),
        migrations.CreateModel(
            name='Textures',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='3d texture 파일 아이디')),
                ('fileDir', models.CharField(blank=True, max_length=500, null=True, verbose_name='texture 파일 경로')),
                ('size', models.BigIntegerField(default=0, verbose_name='파일 사이즈')),
                ('d3ObjId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='processing.objects3d', verbose_name='3D 오브젝트 아이디')),
            ],
            options={
                'verbose_name': 'texture 파일',
                'verbose_name_plural': 'texture 파일',
                'db_table': 'texture',
            },
        ),
    ]
