from django.db import models

# Create your models here.
# =========================MOSAIC=====================================
class Mosaics(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False, verbose_name="모자익 아이디")
    email = models.ForeignKey('users.Users', to_field='email', on_delete=models.CASCADE, verbose_name='이메일',
                              db_column='email')
    projectId = models.ForeignKey('projects.Projects', db_column='projectId', on_delete=models.CASCADE,
                                  verbose_name='프로젝트 아이디')
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name='모자익 생성 일자')
    modified = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name='모자익 수정 일자')
    volume = models.BigIntegerField(default=0, verbose_name='용량')
    mosaicDir = models.CharField(max_length=500, null=False, blank=False, verbose_name='이미지 모자익 파일 경로')
    dsmDir = models.CharField(max_length=500, null=False, blank=False, verbose_name='dsm 파일 경로')
    dsmConvertedDir = models.CharField(max_length=500, null=True, blank=True, verbose_name='dsm 변환 파일 경로')
    dsmBound = models.JSONField(null=True, blank=True, default=list, verbose_name='dsm 영상 boundary')
    coordSystem = models.CharField(max_length=50, null=False, blank=False, verbose_name='좌표계 정보')
    mosaicSize = models.BigIntegerField(default=0, null=False, blank=False, verbose_name='모자익 파일 사이즈')
    dsmSize = models.BigIntegerField(default=0, null=False, blank=False, verbose_name='dsm 파일 사이즈')
    bounds = models.JSONField(null=False, blank=False, default=list, verbose_name='모자익 영상 boundary')
    gsd = models.FloatField(null=False, blank=False, default=0, verbose_name='gsd')
    voxelDir = models.CharField(max_length=400, blank=True, null=True, verbose_name="복셀 파일 경로")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'mosaic'
        unique_together = ('id', 'projectId', 'email')
        verbose_name = '모자익'
        verbose_name_plural = '모자익'
        ordering = ['-id']

# =========================MOSAIC=====================================

# =========================3DOBJECT===================================

class Objects3D(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name='3d 오브젝트 아이디')
    projectId = models.ForeignKey('projects.Projects', on_delete=models.CASCADE, verbose_name='프로젝트 아이디')
    pcdFile = models.CharField(max_length=500, null=True, blank=True, verbose_name='Point Cloud 파일 경로')
    pcdConvertedFile = models.CharField(max_length=500, null=True, blank=True, verbose_name='Point Cloud Converted 파일 경로')
    meshFile = models.CharField(max_length=500, null=True, blank=True, verbose_name='메쉬 파일 경로')
    pcdSize = models.BigIntegerField(default=0, null=False, blank=False, verbose_name='Point Cloud 파일 사이즈')
    meshSize = models.BigIntegerField(default=0, null=False, blank=False, verbose_name='메쉬 파일 사이즈')
    email = models.ForeignKey('users.Users', to_field='email', on_delete=models.CASCADE, verbose_name='이메일',
                              db_column='email')
    contourFile = models.CharField(max_length=500, null=True, blank=True, verbose_name='등고선 파일 경로')
    offsetXYZ = models.JSONField(null=False, blank=False, default=list, verbose_name='model offset')
    coordSystem = models.CharField(max_length=200, null=False, blank=False, default="4326", verbose_name='좌표계')
    calibrated_external_camera_parameters = models.CharField(max_length=200, null=True, blank=True, verbose_name='calibrated external camera parameters 경로')
    def __str__(self):
        return str(id)

    class Meta:
        db_table = 'object3d'
        # managed = False  # 이미 설계된 DB가 존재할때
        verbose_name = '3d 데이터'
        verbose_name_plural = '3d 데이터'


# =========================3DOBJECT===================================

# =========================MTL FILE===================================
class Mtls(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='3d mtl 파일 아이디')
    fileDir = models.CharField(max_length=500, null=True, blank=True, verbose_name='mtl 파일 경로')
    projectId = models.ForeignKey('projects.Projects', on_delete=models.CASCADE, verbose_name='프로젝트 아이디')
    d3ObjId = models.ForeignKey('Objects3D', on_delete=models.CASCADE, related_name="mtl", verbose_name='3D 오브젝트 아이디')
    size = models.BigIntegerField(default=0, null=False, blank=False, verbose_name='파일 사이즈')
    email = models.ForeignKey('users.Users', to_field='email', on_delete=models.CASCADE, verbose_name='이메일',
                              db_column='email')

    def __str__(self):
        return str(id)

    class Meta:
        db_table = 'mtl'
        # managed = False  # 이미 설계된 DB가 존재할때
        verbose_name = 'mtl 파일'
        verbose_name_plural = 'mtl 파일'


# =========================MTL FILE===================================

# =========================TEXTURE FILE===============================
class Textures(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name='3d texture 파일 아이디')
    fileDir = models.CharField(max_length=500, null=True, blank=True, verbose_name='texture 파일 경로')
    projectId = models.ForeignKey('projects.Projects', on_delete=models.CASCADE, verbose_name='프로젝트 아이디')
    d3ObjId = models.ForeignKey('Objects3D', on_delete=models.CASCADE, related_name="texture", verbose_name='3D 오브젝트 아이디')
    size = models.BigIntegerField(default=0, null=False, blank=False, verbose_name='파일 사이즈')
    email = models.ForeignKey('users.Users', to_field='email', on_delete=models.CASCADE, verbose_name='이메일',
                              db_column='email')

    def __str__(self):
        return str(id)

    class Meta:
        db_table = 'texture'
        # managed = False  # 이미 설계된 DB가 존재할때
        verbose_name = 'texture 파일'
        verbose_name_plural = 'texture 파일'

# =========================TEXTURE FILE===============================

# =========================FAST MOSAIC================================
class FastMosaics(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, blank=False, verbose_name="간편 모자익 아이디")
    email = models.ForeignKey('users.Users', to_field='email', on_delete=models.CASCADE, verbose_name='이메일',
                              db_column='email')
    projectId = models.ForeignKey('projects.Projects', db_column='projectId', on_delete=models.CASCADE,
                                  verbose_name='프로젝트 아이디')
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name='간편 모자익 생성 일자')
    modified = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name='간편 모자익 수정 일자')
    volume = models.BigIntegerField(default=0, verbose_name='용량')
    mosaicDir = models.CharField(max_length=500, null=False, blank=False, verbose_name='간편 이미지 모자익 파일 경로')
    coordSystem = models.CharField(max_length=50, null=False, blank=False, verbose_name='좌표계 정보')
    mosaicSize = models.BigIntegerField(default=0, null=False, blank=False, verbose_name='모자익 파일 사이즈')
    bounds = models.JSONField(null=False, blank=False, default=list, verbose_name='모자익 영상 boundary')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'fast_mosaic'
        unique_together = ('id', 'projectId', 'email')
        verbose_name = '간편 모자익'
        verbose_name_plural = '간편 모자익'
        ordering = ['-id']
# =========================FAST MOSAIC================================