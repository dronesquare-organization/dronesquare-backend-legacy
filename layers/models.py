from django.contrib.gis.db import models

# Create your models here.

# =========================LAYERS2D===================================
class Layers2D(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="레이어 아이디")
    imgId = models.ForeignKey(
        "imgs.Imgs", on_delete=models.CASCADE, verbose_name="이미지 아이디"
    )
    projectId = models.ForeignKey(
        "projects.Projects", on_delete=models.CASCADE, verbose_name="프로젝트 아이디"
    )
    properties = models.JSONField(default=list, verbose_name="레이어 속성 값")
    email = models.ForeignKey(
        "users.Users", to_field="email", on_delete=models.CASCADE, verbose_name="이메일"
    )
    created = models.DateTimeField(
        auto_now_add=True, null=False, blank=False, verbose_name="레이어 생성 시간"
    )
    modified = models.DateTimeField(
        auto_now=True, null=False, blank=False, verbose_name="레이어 수정 시간"
    )
    issueCnt = models.IntegerField(
        default=0, null=False, blank=False, verbose_name="이슈 개수"
    )

    def __str__(self):
        return str(id)

    class Meta:
        db_table = "layers2d"
        # managed = False  # 이미 설계된 DB가 존재할때
        verbose_name = "2d 레이어 정보"
        verbose_name_plural = "2d 레이어 정보들"
        ordering = ["imgId"]


# =========================LAYERS2D===================================

# =========================LAYERS2D&3D================================
class Layers2D3D(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="2d3d 레이어 아이디")
    projectId = models.ForeignKey(
        "projects.Projects",
        to_field="id",
        on_delete=models.CASCADE,
        verbose_name="프로젝트 아이디",
    )
    mosaicId = models.ForeignKey(
        "processing.Mosaics", on_delete=models.CASCADE, verbose_name="모자익 아이디"
    )
    properties = models.JSONField(verbose_name="레이어 속성 값")
    email = models.ForeignKey(
        "users.Users", to_field="email", on_delete=models.CASCADE, verbose_name="이메일"
    )
    created = models.DateTimeField(
        auto_now_add=True, null=False, blank=False, verbose_name="레이어 생성 시간"
    )
    modified = models.DateTimeField(
        auto_now=True, null=False, blank=False, verbose_name="레이어 수정 시간"
    )

    def __str__(self):
        return str(id)

    class Meta:
        db_table = "layers2d3d"
        verbose_name = "2d3d 레이어 정보"
        verbose_name_plural = "2d3d 레이어 정보들"


# =========================LAYERS2D&3D================================
# =========================LAYERS3D===================================
class Layers3D(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="3d 레이어 아이디")
    projectId = models.ForeignKey(
        "projects.Projects",
        to_field="id",
        on_delete=models.CASCADE,
        verbose_name="프로젝트 아이디",
    )
    fileDir = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="mtl 파일 경로"
    )
    projectId = models.ForeignKey(
        "projects.Projects", on_delete=models.CASCADE, verbose_name="프로젝트 아이디"
    )
    ObjId = models.ForeignKey(
        "processing.Objects3D",
        on_delete=models.CASCADE,
        related_name="layer3d",
        verbose_name="3D 오브젝트 아이디",
    )
    size = models.BigIntegerField(
        default=0, null=False, blank=False, verbose_name="파일 사이즈"
    )
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
        db_column="email",
    )

    def __str__(self):
        return str(id)

    class Meta:
        db_table = "layers3d"
        verbose_name = "3d 레이어 정보"
        verbose_name_plural = "3d 레이어 정보들"


# =========================LAYERS3D===================================

# =========================LAYER MTL FILE=============================
class LayerMtls(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="3d mtl 파일 아이디")
    fileDir = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="mtl 파일 경로"
    )
    projectId = models.ForeignKey(
        "projects.Projects", on_delete=models.CASCADE, verbose_name="프로젝트 아이디"
    )
    layerId = models.ForeignKey(
        "Layers3D",
        on_delete=models.CASCADE,
        related_name="layermtl",
        verbose_name="3D 레이어 아이디",
    )
    size = models.BigIntegerField(
        default=0, null=False, blank=False, verbose_name="파일 사이즈"
    )
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
        db_column="email",
    )

    def __str__(self):
        return str(id)

    class Meta:
        db_table = "layer_mtl"
        # managed = False  # 이미 설계된 DB가 존재할때
        verbose_name = "layer mtl 파일"
        verbose_name_plural = "layer mtl 파일"


# =========================LAYER MTL FILE=============================

# =========================LAYER TEXTURE FILE=========================
class LayerTextures(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="3d texture 파일 아이디")
    fileDir = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="texture 파일 경로"
    )
    projectId = models.ForeignKey(
        "projects.Projects", on_delete=models.CASCADE, verbose_name="프로젝트 아이디"
    )
    layerId = models.ForeignKey(
        "Layers3D",
        on_delete=models.CASCADE,
        related_name="layertexture",
        verbose_name="3D 레이어 아이디",
    )
    size = models.BigIntegerField(
        default=0, null=False, blank=False, verbose_name="파일 사이즈"
    )
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
        db_column="email",
    )

    def __str__(self):
        return str(id)

    class Meta:
        db_table = "layer_texture"
        # managed = False  # 이미 설계된 DB가 존재할때
        verbose_name = "layer texture 파일"
        verbose_name_plural = "layer texture 파일"


# =========================LAYER TEXTURE FILE=========================
