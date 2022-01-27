# Python Libraries
import re

# Django Apis
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt

# Project Apps
from .models import Users, Storages, Payment
from .serializers import (
    CustomRegisterSerializer,
    UserAdditionalSerializer,
    StorageSerializer,
    CurrentUserSerializer,
    UserPasswordFormSerializer,
    PaymentSerializer,
    MyTokenObtainPairSerializer,
)
from .tokens import account_activation_token

# Third Party Packages
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

# =========================USER=======================================
class RegistrationViewSet(viewsets.ViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="회원가입",
        request_body=CustomRegisterSerializer,
        manual_parameters=[],
    )
    @csrf_exempt
    def create(self, request):
        request.data["is_active"] = False
        serializer = CustomRegisterSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save(request)
            mail_subject = "이메일 인증을 완료해주세요"
            token = account_activation_token.make_token(user)
            FRONTEND_URL = settings.FRONTEND_URL
            verify_link = (
                FRONTEND_URL
                + "/email-verify/"
                + urlsafe_base64_encode(force_bytes(user.pk)).encode().decode()
                + "/"
                + token
            )
            html_content = render_to_string(
                "verify_email.html",
                {"verify_link": verify_link, "base_url": FRONTEND_URL},
            )
            text_content = strip_tags(html_content)
            from_email = "no-reply@drone.com"
            msg = EmailMultiAlternatives(
                mail_subject, text_content, from_email, [request.data["email"]]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return Response(
                {"message": "Confirm your Email"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_200_OK)


class EmailActiveViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="이메일 인증",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "uid": openapi.Schema(type=openapi.TYPE_STRING, description="uid"),
                "token": openapi.Schema(type=openapi.TYPE_STRING, description="토큰"),
            },
        ),
        manual_parameters=[],
    )
    def create(self, request):
        token = request.data["token"]
        uid = request.data["uid"]
        try:
            uid = force_text(urlsafe_base64_decode(uid))
            user = Users.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "success"})
        else:
            return Response({"message": "invalid"})


class CheckingEmailViewSet(viewsets.ViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="이메일 중복 확인",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="email")
            },
        ),
        manual_parameters=[],
    )
    @csrf_exempt
    def create(self, request):
        validator = re.compile("^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        try:
            if validator.match(request.data["email"]) is None:
                return Response({"message": "invalid"})
            user = Users.objects.get(email=request.data["email"])
            return Response({"message": "Duplicate"})
        except Users.DoesNotExist:
            return Response({"message": "Available"})


class UserInfoViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 회원 정보 가져오기",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def list(self, request):
        email = str(request.user)
        query_set = Users.objects.all()
        # return Response()
        user = get_object_or_404(query_set, email=email)
        serializer = CurrentUserSerializer(user)
        return Response(serializer.data)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 회원 정보 수정",
        request_body=UserAdditionalSerializer,
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def create(self, request):
        email = request.user
        query_set = Users.objects.all()
        user = get_object_or_404(query_set, email=email)
        serializer = UserAdditionalSerializer(
            user, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserPasswordViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 회원 비밀번호 변경",
        request_body=UserPasswordFormSerializer,
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def partial_update(self, request, pk=None):
        if request.data["password"] != request.data["password1"]:
            return Response(
                {"message": "Password is not Same"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        if check_password(request.data["current_password"], user.password):
            try:
                password_validation.validate_password(request.data["password"])
                user.set_password(request.data["password"])
                user.save()
                return Response(status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response(e, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "current password is not valid"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(APIView):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 회원 로그 아웃",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh_token": openapi.Schema(
                    type=openapi.TYPE_STRING, description="리프레쉬 토큰"
                )
            },
        ),
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# =========================USER=======================================

# =========================STORAGES===================================
class StorageDetailViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 회원 용량 확인",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def list(self, request):
        email = str(request.user)
        query_set = Storages.objects.all()
        # return Response()
        storageByEmail = get_object_or_404(query_set, email=email)
        serializer = StorageSerializer(storageByEmail)
        return Response(serializer.data)


# =========================STORAGES===================================

# =========================PAYMENT====================================
class PaymentViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 회원 모든 계좌 확인",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def list(self, request):
        email = str(request.user)
        paymentByEmail = Payment.objects.filter(email=email)
        serializer = PaymentSerializer(paymentByEmail, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 회원 모든 계좌 확인",
        request_body=PaymentSerializer,
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def create(self, request):
        email = str(request.user)
        if request.data["email"] != email:
            return Response(
                {"message": "unAuthorized"}, status=status.HTTP_400_BAD_REQUEST
            )
        request.data["email"] = email
        serializer = PaymentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "fail"}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 회원의 해당 계좌 정보 변경",
        request_body=PaymentSerializer,
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def partial_update(self, request, pk):
        email = str(request.user)
        if request.data["email"] != email:
            return Response(
                {"message": "unAuthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        query_set = Payment.objects.all()
        payment = get_object_or_404(query_set, id=pk)
        serializer = PaymentSerializer(
            payment, data=request.data, context={"request": request}
        )
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 회원의 해당 계좌 삭제",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def destroy(self, request, pk):
        email = str(request.user)
        query_set = Payment.objects.all()
        payment = get_object_or_404(query_set, id=pk)
        serializer = PaymentSerializer(payment)
        if serializer.data["email"] != email:
            return Response(
                {"message": "unAuthorized"}, status=status.HTTP_400_BAD_REQUEST
            )
        payment.delete()
        return Response()


# =========================PAYMENT====================================
