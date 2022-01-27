# Python Libraries
import os

# Django Apis
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.storage import FileSystemStorage
from django.db import models

# Project Apps
from .managers import UserManager
from backendAPI import settings


# =========================USER=======================================
class OverwriteStorage(FileSystemStorage):
    """
    file duplicate check
    """

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class Users(AbstractBaseUser, PermissionsMixin):
    username = None

    SECTOR_TYPE_CHOICES = (
        ("건축", "건축"),
        ("토목", "토목"),
        ("안전진단", "안전진단"),
        ("서비스업", "서비스업"),
        ("기타", "기타"),
    )
    id = models.BigAutoField(
        primary_key=True, null=False, blank=False, verbose_name="유저 인덱스"
    )
    email = models.EmailField(
        unique=True, max_length=200, null=False, blank=False, verbose_name="이메일"
    )
    name = models.CharField(max_length=200, null=False, blank=False, verbose_name="이름")
    password = models.CharField(
        max_length=200, null=False, blank=False, verbose_name="비밀번호"
    )
    plan = models.CharField(
        default="FREE", max_length=200, null=False, blank=False, verbose_name="플랜"
    )
    phoneNumber = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        db_column="phone_number",
        verbose_name="연락처",
    )
    sectors = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        default="기타",
        choices=SECTOR_TYPE_CHOICES,
        db_column="sectors",
        verbose_name="업종",
    )
    organization = models.CharField(
        max_length=200, null=False, blank=False, verbose_name="조직 이름"
    )
    planEnrollmentDate = models.DateTimeField(
        null=False,
        blank=False,
        db_column="plan_enrollment_date",
        auto_now_add=True,
        verbose_name="플랜 등록 일자",
    )
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phoneNumber", "organization"]

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자"
        ordering = ["-date_joined"]


# =========================USER=======================================

# =========================STORAGE====================================
class Storages(models.Model):
    email = models.OneToOneField(
        "Users",
        to_field="email",
        primary_key=True,
        db_column="email",
        on_delete=models.CASCADE,
        verbose_name="이메일",
    )
    gigaPixel = models.BigIntegerField(
        db_column="giga_pixel", default=0, verbose_name="기가 픽셀"
    )
    pic = models.BigIntegerField(default=0, verbose_name="사진 용량")
    vid = models.BigIntegerField(default=0, verbose_name="비디오 용량")
    doc = models.BigIntegerField(default=0, verbose_name="도큐먼트 용량")
    others = models.BigIntegerField(default=0, verbose_name="기타 용량")

    class Meta:
        db_table = "storages"
        verbose_name = "용량"
        verbose_name_plural = "용량"


# =========================STORAGE====================================

# =========================PAYMENT====================================
class Payment(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="계좌 정보 인덱스")
    account = models.CharField(
        max_length=355, null=False, blank=False, verbose_name="계좌 번호"
    )
    email = models.ForeignKey(
        "Users",
        to_field="email",
        on_delete=models.CASCADE,
        db_column="email",
        verbose_name="이메일",
    )
    bank = models.CharField(max_length=50, null=False, blank=False, verbose_name="은행")

    class Meta:
        db_table = "payment"
        unique_together = (("email", "account", "bank"),)
        verbose_name = "계좌 정보"
        verbose_name_plural = "계좌 정보"


# =========================PAYMENT====================================
