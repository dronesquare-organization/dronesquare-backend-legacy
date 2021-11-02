from django.contrib.gis.db import models

# Create your models here.
# =========================PROJECTS===================================
from django.core.files.storage import FileSystemStorage

from backendAPI import settings


class Projects(models.Model):
    ASSET_TYPE_CHOICES = (
        ("도로", "도로"),
        ("건물", "건물"),
        ("항만", "항만"),
        ("기타", "기타"),
    )
    INFRA_TYPE_CHOICES = (
        ("일반 객체", "일반 객체"),
        ("코리더(Corridor) 객체", "코리더(Corridor) 객체"),
        ("면 객체", "면 객체"),
        ("수직 객체", "수직 객체"),
        ("기타", "기타"),
    )
    UPLOAD_TYPE_CHOICES = (
        ("처리전", "처리전"),
        ("진행중", "진행중"),
        ("완료", "완료"),
    )

    id = models.BigAutoField(
        primary_key=True, null=False, blank=False, verbose_name="프로젝트 아이디"
    )
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
        db_column="email",
    )
    areaName = models.CharField(
        max_length=200,
        db_column="area_name",
        null=False,
        blank=False,
        verbose_name="지역 이름",
    )
    assetName = models.CharField(
        max_length=200,
        db_column="asset_name",
        null=False,
        blank=False,
        verbose_name="구조물 이름",
    )
    assetType = models.CharField(
        default="기타",
        max_length=200,
        db_column="asset_type",
        choices=INFRA_TYPE_CHOICES,
        null=False,
        blank=False,
        verbose_name="인프라 타입",
    )
    projectName = models.CharField(
        max_length=200, db_column="name", null=False, blank=False, verbose_name="지역 이름"
    )
    created = models.DateTimeField(
        auto_now_add=True, null=False, blank=False, verbose_name="프로젝트 생성 일자"
    )
    modified = models.DateTimeField(
        auto_now=True, null=False, blank=False, verbose_name="프로젝트 수정 일자"
    ) 
    coordinateSystem = models.CharField(
        default="EPSG:3857",
        max_length=200,
        db_column="coordinate_system",
        verbose_name="좌표 체계",
    )
    shared = models.BooleanField(
        default=False, null=True, blank=True, verbose_name="공유 여부"
    )
    imgCnt = models.IntegerField(
        default=0, db_column="img_cnt", null=False, blank=False, verbose_name="이미지 수"
    )
    comment = models.TextField(null=True, blank=True, verbose_name="프로젝트에 대한 코멘트")
    location = models.PointField(
        null=False, blank=False, srid=4326, verbose_name="프로젝트 위치"
    )
    uploading = models.CharField(
        default="처리전", max_length=50, null=False, blank=False, choices=UPLOAD_TYPE_CHOICES, verbose_name="업로딩 여부"
    )
    imgVolume = models.BigIntegerField(default=0, verbose_name="프로젝트 이미지 용량")
    videoVolume = models.BigIntegerField(default=0, verbose_name="프로젝트 비디오 용량")
    etcVolume = models.BigIntegerField(default=0, verbose_name="프로젝트 기타 파일 용량")
    pcdVolume = models.BigIntegerField(default=0, verbose_name="프로젝트 포인트 클라우드 용량")
    mosaicVolume = models.BigIntegerField(default=0, verbose_name="프로젝트 모자익 용량")
    meshVolume = models.BigIntegerField(default=0, verbose_name="프로젝트 메쉬 용량")
    img_created = models.DateTimeField(null=True, blank=True, verbose_name="이미지 생성 시간")
    area = models.FloatField(default=0, verbose_name="프로젝트 면적")
    issueCnt = models.IntegerField(default=0, verbose_name="총 이슈 개수")
    timeSeriesCnt = models.IntegerField(default=0, verbose_name="시계열 연계 개수")
    isRtk = models.BooleanField(default=False, verbose_name="RTK 유무")
    duplicate_rate = models.FloatField(default=0, verbose_name="중복도")
    duplicate_std = models.FloatField(default=0, verbose_name="중복도 편차")


    def __str__(self):
        return str(self.id)

    class Meta:

        db_table = "projects"
        unique_together = (("id", "email"),)
        verbose_name = "프로젝트"
        verbose_name_plural = "프로젝트"
        ordering = ["-id"]


# =========================PROJECTS===================================

# =========================ANOMALY-TYPE==============================
def anomalyType_default_value():  # This is a callable
    return [
        "메모", "균열", "부식", "녹슴", "손실", "변형", "누수", "안전위험", "잔해", "핫스팟", "간섭", "기타"
      ]
class AnomalyTypes(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="이슈 타입 아이디")
    projectId = models.ForeignKey(
        "Projects",
        related_name="anomaly_types",
        on_delete=models.CASCADE,
        db_column="projectId",
        verbose_name="프로젝트 아이디",
    )
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
        db_column="email",
        default=""
    )
    types = models.JSONField(null=False, blank=False, default=anomalyType_default_value, verbose_name='이슈 타입')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "anomaly_types"
        verbose_name = "이슈 타입"
        verbose_name_plural = "이슈 타입들"

# =========================ANOMALY-TYPE==============================

# =========================ANOMALY-DEGREE============================
def anomalyType_default_value():  # This is a callable
    return [
        "심각도", "중요도", "긴급도"
      ]
class AnomalyDegree(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="이슈 정도 아이디")
    projectId = models.ForeignKey(
        "Projects",
        related_name="anomaly_degree",
        on_delete=models.CASCADE,
        db_column="projectId",
        verbose_name="프로젝트 아이디",
    )
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
        db_column="email",
        default=""
    )
    types = models.JSONField(null=False, blank=False, default=anomalyType_default_value, verbose_name='이슈 정도')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "anomaly_degree"
        verbose_name = "이슈 정도"
        verbose_name_plural = "이슈 정도들"
# =========================ANOMALY-DEGREE============================

# =========================DATA-PROCESS==============================
class DataProcess(models.Model):
    UPLOAD_TYPE_CHOICES = (
        ("처리전", "처리전"),
        ("접수중", "접수중"),
        ("진행중", "진행중"),
        ("처리완료", "처리완료"),
        ("보완요구", "보완요구"),
    )
    COORDINATE_TYPE_CHOICES = (
        ("EPSG:4326","EPSG:4326"),   #WGS84경위도
        ("EPSG:3857","EPSG:3857"),   #WGS84경위도(m 단위)
        ("EPSG:32652","EPSG:32652"), #UTM52N(WGS84)
        ("EPSG:32651","EPSG:32651"), #UTM51N(WGS84)
        ("EPSG:5186","EPSG:5186"),   #중부원점(GRS80)
        ("EPSG:5187","EPSG:5187"),   #동부원점(GRS80)
    )
    id = models.BigAutoField(primary_key=True, verbose_name="데이터가공 아이디")
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
        db_column="email",
    )
    projectId = models.OneToOneField(
        "Projects",
        on_delete=models.CASCADE,
        db_column="projectId",
        related_name="dataprocess",
        verbose_name="프로젝트 아이디",
    )
    processStatus = models.CharField(
        default="처리전",
        max_length=50,
        null=True,
        blank=True,
        db_column="process_Status",
        choices=UPLOAD_TYPE_CHOICES,
        verbose_name="데이터 프로세스 처리 상태값",
    )
    applyProcess = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        db_column="apply_data_process",
        verbose_name="데이터 프로세스 신청 날짜",
    )
    completedProcess = models.DateTimeField(
        auto_now_add=False,
        null=True,
        blank=True,
        db_column="completed_data_process",
        verbose_name="데이터 프로세스 완료 날짜",
    )
    notice = models.TextField(default="", null=True, blank=True, verbose_name="알림 메모")
    quality_low = models.IntegerField(default=0, null=True, blank=True, verbose_name="low 퀄리티 시간")
    quality_high = models.IntegerField(default=0, null=True, blank=True, verbose_name="high 퀄리티 시간")
    quality_mid = models.IntegerField(default=0, null=True, blank=True, verbose_name="mid 퀄리티 시간")
    quality = models.CharField(max_length=50, null=True, blank=True, verbose_name="선택된 퀄리티")
    gsd = models.FloatField(null=False, blank=False, default=0, verbose_name='gsd')
    mosaicResolution = models.FloatField(default=0, verbose_name="정사영상 해상도")
    pointDensity = models.FloatField(default=0, verbose_name="점밀도")
    precision_x = models.FloatField(default=0, verbose_name="x축 정밀도")
    precision_y = models.FloatField(default=0, verbose_name="y축 정밀도")
    precision_z = models.FloatField(default=0, verbose_name="z축 정밀도")
    precision_rmse = models.FloatField(default=0, verbose_name="RMSE")
    coordinateSystem = models.CharField(
        default="EPSG:4326",
        max_length=200,
        null=True,
        blank=True,
        choices=COORDINATE_TYPE_CHOICES,
        db_column="coordinate_system",
        verbose_name="좌표 체계",
    )
    admin_download = models.BooleanField(default=False, verbose_name="관리자 다운로드")
    admin_upload = models.BooleanField(default=False, verbose_name="관리자 업로드")
    processOption = models.CharField(max_length=50, default="", null=True, blank=True, verbose_name="프로세스 옵션")
    request_memo = models.TextField(default="", null=True, blank=True, verbose_name="요청 사항")

    class Meta:
        db_table = "dataprocess"
        unique_together = (("projectId", "id", "email"),)
        verbose_name = "데이터 가공"
        verbose_name_plural = "데이터 가공"
        ordering = ["-id"]

# =========================DATA-PROCESS==============================

# =========================DARA-PROCESS-FILE=========================
class DataProcessFile(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="데이터가공 파일 아이디")
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
        db_column="email",
    )
    projectId = models.ForeignKey(
        "Projects",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_column="projectId",
        verbose_name="프로젝트 아이디",
    ),
    dataprocessId = models.ForeignKey(
        "DataProcess",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_column="dataprocessId",
        verbose_name="데이터 프로세스 아이디"
    )
    name = models.CharField(
        max_length=200, null=False, blank=False, verbose_name="파일 이름"
    )
    format = models.CharField(max_length=10, null=False, blank=False, verbose_name="포맷")
    created = models.DateTimeField(null=False, blank=False, verbose_name="파일 생성 일자")
    size = models.IntegerField(null=False, blank=False, verbose_name="파일 크기")
    fileDir = models.CharField(
        max_length=400, null=True, blank=True, verbose_name="피일 경로"
    )
    fileType = models.CharField(max_length=100, null=False, blank=False, verbose_name="데이터 가공 파일 종류")


    def __str__(self):
            return str(self.projectId)

    class Meta:
        db_table = "dataprocess_file"
        unique_together = (("id", "name", "format"),)
        verbose_name = "데이터 가공 파일첨부"
        verbose_name_plural = "데이터 가공 파일첨부"
        ordering = ["created"]

# =========================DARA-PROCESS-FILE=========================