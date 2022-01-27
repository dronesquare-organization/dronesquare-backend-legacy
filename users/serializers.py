from drf_braces.serializers.form_serializer import FormSerializer
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from .forms import ChangePasswordForm
from .models import Users, Storages, Payment

# =========================USER=======================================
"""
    User Serializer
"""


# rest-auth register serializer
class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    name = serializers.CharField(required=True)
    phoneNumber = serializers.CharField(required=True)
    organization = serializers.CharField(required=True)
    sectors = serializers.CharField(required=True)
    username = None

    def get_cleaned_data(self):
        return {
            "password1": self.validated_data.get("password1", ""),
            "password2": self.validated_data.get("password2", ""),
            "email": self.validated_data.get("email", ""),
            "name": self.validated_data.get("name", ""),
            "phoneNumber": self.validated_data.get("phoneNumber", ""),
            "organization": self.validated_data.get("organization", ""),
            "sectors": self.validated_data.get("sectors", ""),
        }


# rest-auth register additional information serializer
class CustomUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ("email", "name", "phoneNumber", "organization")
        read_only_fields = ("email", "name", "phoneNumber", "organization")


# user info serializer
class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = (
            "id",
            "email",
            "name",
            "phoneNumber",
            "organization",
            "plan",
            "sectors",
        )


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            refresh = self.get_token(self.user)
            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)
            return data
        except Exception:
            return {"message": "invalid"}


# user additional info serializer
class UserAdditionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ("name", "phoneNumber", "organization", "sectors")


# user plan change serializer
class UserPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ("email", "plan")


# user password change
class UserPasswordFormSerializer(FormSerializer):
    class Meta:
        form = ChangePasswordForm


# =========================USER=======================================

# =========================STORAGES===================================
"""
    Storage Serializer
"""


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storages
        fields = "__all__"


class StorageFindSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storages
        fields = ("email",)


# =========================STORAGES===================================

# =========================PAYMENT====================================
"""
    Payment Serializer
"""


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


# =========================PAYMENT====================================
