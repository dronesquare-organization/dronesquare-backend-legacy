from django.contrib.gis.db import models
from utils.SetUploadPath import originalImg_upload_path, compressionImg_upload_path, thunmbnailImg_upload_path
from django.core.files.storage import FileSystemStorage

# Create your models here.
# =========================IMGS=======================================
class OverwriteStorage(FileSystemStorage):
    """
    file duplicate check
    """

    def get_available_name(self, name, max_length=None):
        print("here   ", name)
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class Imgs(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="이미지 아이디")
    projectId = models.ForeignKey(
        "projects.Projects",
        related_name="imgs",
        on_delete=models.CASCADE,
        db_column="projectId",
        verbose_name="프로젝트 아이디",
    )
    name = models.CharField(
        max_length=200, null=False, blank=False, verbose_name="이미지 이름"
    )
    format = models.CharField(max_length=10, null=False, blank=False, verbose_name="포맷")
    created = models.DateTimeField(null=False, blank=False, verbose_name="이미지 생성 일자")
    modified = models.DateTimeField(null=False, blank=False, verbose_name="이미지 변경 일자")
    size = models.IntegerField(null=False, blank=False, verbose_name="파일 크기")
    fileDir = models.ImageField(upload_to=compressionImg_upload_path, null=True, blank=True, verbose_name="피일 경로")
    annotationCnt = models.IntegerField(
        default=0, null=False, blank=False, verbose_name="도식 수"
    )
    width = models.IntegerField(null=False, blank=False, verbose_name="이미지 가로 픽셀")
    height = models.IntegerField(null=False, blank=False, verbose_name="이미지 세로 픽셀")
    thumbnail = models.ImageField(upload_to=thunmbnailImg_upload_path, null=True, blank=True, verbose_name="썸네일 경로"
    )
    location = models.PointField(
        null=True, blank=True, srid=4326, verbose_name="사진 GPS 위치"
    )
    focalLength = models.FloatField(null=True, blank=True)
    make = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="카메라 제작사"
    )
    model = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="카메라 모델"
    )
    fNumber = models.FloatField(null=True, blank=True, verbose_name="F Number")
    focalLengthIn35mmFilm = models.FloatField(
        null=True, blank=True, verbose_name="35mm 기준 focal length"
    )
    altitude = models.FloatField(null=True, blank=True, verbose_name="이미지 고도")
    # isOptimized = models.BooleanField(default=False, verbose_name="이미지 중첩 최적화 여부")
    isOptimized = models.BooleanField(default=True, verbose_name="이미지 중첩 최적화 여부")
    isDibs = models.BooleanField(default=False, verbose_name="이미지 찜 여부")
    filterDir = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="필터 적용 결과 경로"
    )
    illuminationDelta = models.FloatField(default=0, verbose_name="이미지 명암 계수")
    autoDelta = models.FloatField(default=0, verbose_name="이미지 자동 명암 계수")
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        on_delete=models.CASCADE,
        db_column="email",
        verbose_name="이메일",
    )
    iSOSpeedRatings = models.IntegerField(null=True, blank=True, verbose_name="ISO 감도")

    def __str__(self):
        return str(self.projectId)

    def getFullName(self):
        return self.name + "." + self.format

    class Meta:

        db_table = "imgs"
        unique_together = (("projectId", "id", "name", "format"),)
        verbose_name = "이미지"
        verbose_name_plural = "이미지"
        ordering = ["created"]


# =========================IMGS=======================================