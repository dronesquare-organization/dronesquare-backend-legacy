import os

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.storage import FileSystemStorage
from django.db import models

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


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    use_in_migrations = True

    def create_user(self, email, name, phoneNumber, organization, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phoneNumber=phoneNumber,
            organization=organization,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, name, phoneNumber, organization, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phoneNumber=phoneNumber,
            organization=organization,
            **extra_fields
        )
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, name, phoneNumber, organization, password, **extra_fields)


# Create your models here.
class Users(AbstractBaseUser, PermissionsMixin):
    username = None

    SECTOR_TYPE_CHOICES = (
        ("??????","??????"),
        ("??????","??????"),   
        ("????????????","????????????"), 
        ("????????????","????????????"), 
        ("??????","??????"),   
    )
    id = models.BigAutoField(primary_key=True, null=False, blank=False, verbose_name="?????? ?????????")
    email = models.EmailField(unique=True, max_length=200, null=False, blank=False, verbose_name="?????????")
    name = models.CharField(max_length=200, null=False, blank=False, verbose_name="??????")
    password = models.CharField(max_length=200, null=False, blank=False, verbose_name="????????????")
    plan = models.CharField(default='FREE', max_length=200, null=False, blank=False, verbose_name="??????")
    phoneNumber = models.CharField(max_length=20, null=False, blank=False, db_column="phone_number", verbose_name="?????????")
    sectors = models.CharField(max_length=200, null=False, blank=False, default="??????", choices=SECTOR_TYPE_CHOICES, db_column="sectors", verbose_name="??????")
    organization = models.CharField(max_length=200, null=False, blank=False, verbose_name="?????? ??????")
    planEnrollmentDate = models.DateTimeField(null=False, blank=False, db_column="plan_enrollment_date",
                                              auto_now_add=True, verbose_name='?????? ?????? ??????')
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phoneNumber', 'organization']

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = '?????????'
        verbose_name_plural = '?????????'
        ordering = ['-date_joined']


# =========================USER=======================================

# =========================STORAGE====================================
class Storages(models.Model):
    email = models.OneToOneField('Users', to_field='email', primary_key=True, db_column='email', on_delete=models.CASCADE,
                                 verbose_name='?????????')
    gigaPixel = models.BigIntegerField(db_column="giga_pixel", default=0, verbose_name='?????? ??????')
    pic = models.BigIntegerField(default=0, verbose_name='?????? ??????')
    vid = models.BigIntegerField(default=0, verbose_name='????????? ??????')
    doc = models.BigIntegerField(default=0, verbose_name='???????????? ??????')
    others = models.BigIntegerField(default=0, verbose_name='?????? ??????')

    class Meta:
        db_table = 'storages'
        verbose_name = '??????'
        verbose_name_plural = '??????'


# =========================STORAGE====================================

# =========================PAYMENT====================================
class Payment(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='?????? ?????? ?????????')
    account = models.CharField(max_length=355, null=False, blank=False, verbose_name='?????? ??????')
    email = models.ForeignKey('Users', to_field='email', on_delete=models.CASCADE, db_column='email',
                              verbose_name='?????????')
    bank = models.CharField(max_length=50, null=False, blank=False, verbose_name='??????')

    class Meta:
        db_table = 'payment'
        unique_together = (('email', 'account', 'bank'),)
        verbose_name = '?????? ??????'
        verbose_name_plural = '?????? ??????'

# =========================PAYMENT====================================
