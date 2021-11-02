from django.db import models

from utils.SetUploadPath import video_upload_path, etc_upload_path, etcImg_upload_path, etcDoc_upload_path, etc2D3D_upload_path, nestedLayer_upload_path, gcp_upload_path
from django.core.files.storage import FileSystemStorage

# Create your models here.
class Video(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="비디오 아이디")
    projectId = models.ForeignKey(
        "projects.Projects",
        on_delete=models.CASCADE,
        db_column="projectId",
        verbose_name="프로젝트 아이디",
    )
    name = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="비디오 파일 이름"
    )
    ext = models.CharField(max_length=200, null=True, blank=True, verbose_name="확장자")
    fileDir = models.FileField(upload_to=video_upload_path, verbose_name="파일 경로")
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        db_column="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
    )
    uploadDate = models.DateTimeField(auto_now_add=True, verbose_name="업로드 시간")
    size = models.BigIntegerField(default=0, verbose_name="용량")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "video"
        verbose_name = "비디오 파일"
        verbose_name_plural = "비디오 파일들"
        ordering = ["-uploadDate"]


# =========================VIDEO======================================

# =========================NestedLayers===============================
class NestedLayers(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="중첩 파일 아이디")
    projectId = models.ForeignKey(
        "projects.Projects",
        on_delete=models.CASCADE,
        db_column="projectId",
        verbose_name="프로젝트 아이디",
    )
    name = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="중첩 파일 이름"
    )
    ext = models.CharField(max_length=300, null=True, blank=True, verbose_name="확장자")
    fileDir = models.FileField(upload_to=nestedLayer_upload_path, verbose_name='파일 경로')
    coordSystem = models.CharField(max_length=50, null=True, blank=True, verbose_name='좌표계 정보')
    convertedDir = models.CharField(max_length=1000, null=True, blank=True, verbose_name='변환 파일 경로')
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        db_column="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
    )
    isNesting = models.BooleanField(default=False, null=False, blank=False, verbose_name="중첩 가능 여부")
    uploadDate = models.DateTimeField(auto_now_add=True, verbose_name="업로드 시간")
    size = models.BigIntegerField(default=0, verbose_name="용량")
    isEnroll = models.BooleanField(default=False, null=False, blank=False, verbose_name="중첩 레이어 등록")
    boundary = models.JSONField(null=True, blank=True, default=list, verbose_name='변환 결과 바운더리')
    
    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "nested_layers"
        verbose_name = "레이어 중첩 파일"
        verbose_name_plural = "레이어 중첩 파일"
        ordering = ["-uploadDate"]
# =========================NestedLayers===============================

# =========================etcImgs====================================
class EtcImgs(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="기타 이미지 파일 아이디")
    projectId = models.ForeignKey(
        "projects.Projects",
        on_delete=models.CASCADE,
        db_column="projectId",
        verbose_name="프로젝트 아이디",
    )
    name = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="기타 이미지 파일 이름"
    )
    ext = models.CharField(max_length=300, null=True, blank=True, verbose_name="확장자")
    fileDir = models.FileField(upload_to=etcImg_upload_path, verbose_name='파일 경로')
    width = models.IntegerField(null=True, blank=True, verbose_name="이미지 가로")
    height = models.IntegerField(null=True, blank=True, verbose_name="이미지 세로")
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        db_column="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
    )
    uploadDate = models.DateTimeField(auto_now_add=True, verbose_name="업로드 시간")
    size = models.BigIntegerField(default=0, verbose_name="용량")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "etc_imgs"
        verbose_name = "기타 이미지 파일"
        verbose_name_plural = "기타 이미지 파일"
        ordering = ["-uploadDate"]
# =========================etcImgs====================================

# =========================etcDocs====================================
class EtcDocs(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="기타 문서 파일 아이디")
    projectId = models.ForeignKey(
        "projects.Projects",
        on_delete=models.CASCADE,
        db_column="projectId",
        verbose_name="프로젝트 아이디",
    )
    name = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="기타 문서 파일 이름"
    )
    ext = models.CharField(max_length=300, null=True, blank=True, verbose_name="확장자")
    fileDir = models.FileField(upload_to=etcDoc_upload_path, verbose_name='파일 경로')
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        db_column="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
    )
    uploadDate = models.DateTimeField(auto_now_add=True, verbose_name="업로드 시간")
    size = models.BigIntegerField(default=0, verbose_name="용량")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "etc_docs"
        verbose_name = "기타 문서 파일"
        verbose_name_plural = "기타 문서 파일"
        ordering = ["-uploadDate"]
# =========================etcDocs====================================

# =========================etc2D3D====================================
class Etc2D3DLayers(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="2d3d 레이어 파일 아이디")
    projectId = models.ForeignKey(
        "projects.Projects",
        on_delete=models.CASCADE,
        db_column="projectId",
        verbose_name="프로젝트 아이디",
    )
    name = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="2d3d 레이어 파일 이름"
    )
    ext = models.CharField(max_length=300, null=True, blank=True, verbose_name="확장자")
    fileDir = models.FileField(upload_to=etcDoc_upload_path, verbose_name='파일 경로')
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        db_column="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
    )
    uploadDate = models.DateTimeField(auto_now_add=True, verbose_name="업로드 시간")
    size = models.BigIntegerField(default=0, verbose_name="용량")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "etc_2d3d_layers"
        verbose_name = "기타 2D&3D 레이어"
        verbose_name_plural = "기타 2D&3D 레이어"
        ordering = ["-uploadDate"]
# =========================etc2D3D====================================

# =========================GCP========================================
class GCP(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="GCP 데이터")
    projectId = models.ForeignKey(
        "projects.Projects",
        on_delete=models.CASCADE,
        db_column="projectId",
        verbose_name="프로젝트 아이디",
    )
    name = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="GCP 파일 이름"
    )
    ext = models.CharField(max_length=300, null=True, blank=True, verbose_name="확장자")
    fileDir = models.FileField(upload_to=gcp_upload_path, verbose_name='파일 경로')
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        db_column="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
    )
    uploadDate = models.DateTimeField(auto_now_add=True, verbose_name="업로드 시간")
    size = models.BigIntegerField(default=0, verbose_name="용량")

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "gcp"
        verbose_name = "GCP 데이터"
        verbose_name_plural = "GCP 데이터"
        ordering = ["-uploadDate"]
# =========================GCP========================================
