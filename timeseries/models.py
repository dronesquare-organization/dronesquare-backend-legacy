from django.db import models

# =========================TIME_SERIES================================
class TimeSeries(models.Model):
    id = models.BigAutoField(
        primary_key=True, null=False, blank=False, verbose_name="시계열 그룹 아이디"
    )
    name = models.CharField(
        max_length=200, null=False, blank=False, verbose_name="시계열 그룹 이름"
    )
    email = models.ForeignKey(
        "users.Users",
        to_field="email",
        on_delete=models.CASCADE,
        db_column="email",
        verbose_name="이메일",
    )
    created = models.DateTimeField(
        auto_now_add=True, null=False, blank=False, verbose_name="시계열 그룹 생성 시간"
    )
    modified = models.DateTimeField(
        auto_now=True, null=False, blank=False, verbose_name="시계열 그룹 수정 시간"
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "timeseries"
        verbose_name = "시계열"
        verbose_name_plural = "시계열"
        ordering = ["created"]


class TimeSeriesRelation(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="시계열 관계 아이디")
    timeseriesId = models.ForeignKey(
        "TimeSeries",
        db_column="timeseriesId",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="relation",
        verbose_name="타임시리즈 아이디",
    )
    projectInfo = models.ForeignKey(
        "projects.Projects",
        db_column="projectInfo",
        related_name="projectInfo",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="프로젝트 아이디",
    )
    email = models.CharField(
        default="",
        null=False,
        blank=False,
        max_length=200,
        db_column="email",
        verbose_name="이메일",
    )

    class Meta:
        db_table = "timeseries_relation"
        unique_together = (("projectInfo", "timeseriesId"),)
        verbose_name = "시계열 매핑"
        verbose_name_plural = "시계열 매핑"


# =========================TIME_SERIES================================
