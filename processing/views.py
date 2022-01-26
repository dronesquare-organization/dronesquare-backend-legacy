# Django Apis
from django.db import transaction

# Project Apps
from .models import Mosaics, Objects3D, FastMosaics
from processing.serializers import (
    MosaicsSerializer,
    Objects3DJoinSerializer,
    FastMosaicsSerializer,
)

# Third Party Packages
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

# utils
from utils.VoxelReader import findFromVoxel

# =========================MOSAICS====================================
class MosaicsViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="모자익 영상 조회",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "projectId",
                openapi.IN_PATH,
                description="PROJECT ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)")
    def mosaic(self, request, projectId):
        email = str(request.user)
        try:
            mosaic = Mosaics.objects.get(email=email, projectId=projectId)
            serializer = MosaicsSerializer(mosaic)
            return Response(serializer.data)
        except Mosaics.DoesNotExist:
            print("mosaic not exist")
            return Response({"message": "not exist"})


class VoxelViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 지점과 관련된 이미지 찾기",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "x": openapi.Schema(type=openapi.TYPE_NUMBER, description="X(Lon) 좌표"),
                "y": openapi.Schema(type=openapi.TYPE_NUMBER, description="Y(Lat) 좌표"),
            },
        ),
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    @action(
        detail=False, methods=["post"], url_path=r"(?P<projectId>\d+)/(?P<mosaicId>\d+)"
    )
    def voxel(self, request, projectId, mosaicId):
        email = str(request.user)
        mosaic = Mosaics.objects.get(email=email, projectId=projectId, id=mosaicId)

        if mosaic is not None:
            if mosaic.voxelDir is None:
                return Response({"message": "empty"})
            result = findFromVoxel([request.data["x"], request.data["y"]], mosaic)
            if result == "empty":
                return Response({"data": {}})
            else:
                return Response({"data": result})
        return Response({"message": "empty"})


# =========================MOSAICS====================================

# =========================3D OBJECTS=================================
class Objects3DViewerViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="3D Object Viewer 정보 가져오기",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)")
    def objects(self, request, projectId):
        email = str(request.user)
        try:
            objects3d = Objects3D.objects.get(email=email, projectId=projectId)
            serializer = Objects3DJoinSerializer(objects3d)
            return Response(serializer.data)
        except Objects3D.DoesNotExist:
            print("object3d not exist")
            return Response({"message": "not exist"})


# =========================3D OBJECTS=================================

# =========================FAST MOSAICS===============================
class FastMosaicsViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="간편 모자익 영상 조회",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "projectId",
                openapi.IN_PATH,
                description="PROJECT ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)")
    def fast_mosaic(self, request, projectId):
        email = str(request.user)
        try:
            mosaic = FastMosaics.objects.get(email=email, projectId=projectId)
            serializer = FastMosaicsSerializer(mosaic)
            return Response(serializer.data)
        except FastMosaics.DoesNotExist:
            print("fast_mosaic not exist")
            return Response({"message": "not exist"})


# =========================FAST MOSAICS===============================
