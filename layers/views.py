# Django Apis
from django.db import transaction
from django.db.models import Sum

# Project Apps
from .models import Layers2D, Layers2D3D
from .serializers import (
    Layers2D3DInputSerializer,
    Layers2D3DListSerializer,
    Layers2D3DSerializer,
    Layers2DInputSerializer,
    Layers2DSerializer,
)
from processing.models import Mosaics
from projects.models import Projects

# Third Party Packages
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# utils
from utils.Calculate3D import (
    calculateByDSM,
    calculateVolume,
    getHighProfile,
    getLocation,
)

# =========================2DLAYERS===================================
class Layers2DViewSet(viewsets.ViewSet):
    @transaction.atomic()
    @swagger_auto_schema(
        operation_description="2D 레이어 생성",
        request_body=Layers2DInputSerializer,
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
        imgId = request.data["imgId"]
        projectId = request.data["projectId"]
        request.data["email"] = email
        request.data["issueCnt"] = len(request.data["properties"])
        query_set = Layers2D.objects.filter(
            email=email, imgId=imgId, projectId=projectId
        )
        serializer = Layers2DSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            if query_set.exists():
                if len(request.data["properties"]) == 0:
                    query_set.delete()
                else:
                    query_set.update(
                        properties=request.data["properties"],
                        issueCnt=len(request.data["properties"]),
                    )
            else:
                serializer.save()

            project = Projects.objects.filter(id=projectId, email=email)
            layerInfo = Layers2D.objects.filter(
                email=email, projectId=projectId
            ).aggregate(sum_of_issueCnt=Sum("issueCnt"))
            project.update(
                issueCnt=layerInfo["sum_of_issueCnt"]
                if layerInfo["sum_of_issueCnt"] is not None
                else 0
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "fail"})

    @transaction.atomic
    @swagger_auto_schema(
        tags=["2d-layers"],
        operation_description="2D 레이어 조회",
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
            openapi.Parameter(
                "imgId",
                openapi.IN_PATH,
                description="IMG ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    @action(
        detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)/(?P<imgId>\d+)"
    )
    def layers(self, request, projectId, imgId):
        email = str(request.user)
        queryset = Layers2D.objects.filter(
            imgId=imgId, projectId=projectId, email=email
        )
        if queryset is not None:
            serializer = Layers2DSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({})

    @transaction.atomic()
    @swagger_auto_schema(
        operation_description="2D 레이어 삭제",
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

        layers = Layers2D.objects.filter(id=pk, email=email)
        if layers is not None:
            layers.delete()
            return Response({"message": "success"})
        return Response({"message": "fail"})


class Layers2DListViewSet(viewsets.ViewSet):
    @transaction.atomic()
    @swagger_auto_schema(
        operation_description="2D 레이어 리스트",
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
    def layers2DList(self, request, projectId):
        email = str(request.user)
        layersData = Layers2D.objects.filter(email=email, projectId=projectId)
        if layersData is not None:
            serializer = Layers2DSerializer(layersData, many=True)
            return Response(serializer.data)
        else:
            return Response()


# =========================2DLAYERS===================================

# =========================2D3DLAYERS=================================
class Layers2D3DViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="2D&3D Layer 생성",
        request_body=Layers2D3DInputSerializer,
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
        request.data["email"] = email

        serializer = Layers2D3DSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"message": "fail"})

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="2D&3D Layer 업데이트",
        request_body=Layers2D3DInputSerializer,
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
        email = request.user
        projectId = request.data["projectId"]
        mosaicId = request.data["mosaicId"]
        layers2d3d = Layers2D3D.objects.get(
            email=email, id=pk, projectId=projectId, mosaicId=mosaicId
        )
        if layers2d3d is not None:
            request.data["email"] = email
            serializer = Layers2D3DSerializer(
                layers2d3d, data=request.data, context={"request": request.data}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response({"message": "fail"})
        return Response({"message": "fail"})

    @swagger_auto_schema(
        tags=["2d-3d-layers"],
        operation_description="2D&3D Layer 삭제",
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
            openapi.Parameter(
                "mosaicId",
                openapi.IN_PATH,
                description="MOSAIC ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "id", openapi.IN_PATH, description="ID", type=openapi.TYPE_INTEGER
            ),
        ],
    )
    @action(
        detail=False,
        methods=["delete"],
        url_path=r"(?P<projectId>\d+)/(?P<mosaicId>\d+)/(?P<id>\d+)",
    )
    def layers2d3d(self, request, projectId, mosaicId, id):
        email = str(request.user)
        layers2d3d = Layers2D3D.objects.get(
            email=email, id=id, projectId=projectId, mosaicId=mosaicId
        )

        if layers2d3d is not None:
            layers2d3d.delete()
            return Response({"message": "success"})
        return Response({"message": "fail"})


class Layers2D3DListViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="2D&3D Layer 리스트조회",
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
            openapi.Parameter(
                "mosaicId",
                openapi.IN_PATH,
                description="MOSAIC ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    @action(
        detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)/(?P<mosaicId>\d+)"
    )
    def layers2d3d_list(self, request, projectId, mosaicId):
        email = str(request.user)
        layers2d3d = Layers2D3D.objects.filter(
            email=email, projectId=projectId, mosaicId=mosaicId
        )
        serializer = Layers2D3DListSerializer(layers2d3d, many=True)

        return Response(serializer.data)


class Layers2D3DPropViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="2D&3D Layer Properties 정보조회",
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
            openapi.Parameter(
                "mosaicId",
                openapi.IN_PATH,
                description="MOSAIC ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    @action(
        detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)/(?P<mosaicId>\d+)"
    )
    def layers2d3d_PropInfoList(self, request, projectId, mosaicId):
        email = str(request.user)
        layers2d3d = Layers2D3D.objects.filter(
            email=email, projectId=projectId, mosaicId=mosaicId
        )
        serializer = D3LayerPropInfoSerializer(layers2d3d, many=True)

        return Response(serializer.data)


# =========================2D3DLAYERS=================================

# =========================CALCULATE3D================================
class LocationViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="해당 지점 z 좌표 가져오기",
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
    def location(self, request, projectId, mosaicId):
        email = str(request.user)
        mosaic = Mosaics.objects.get(email=email, projectId=projectId, id=mosaicId)

        if mosaic is not None:
            result = getLocation([request.data["x"], request.data["y"]], mosaic)
            return Response({"zLoc": result})
        return Response({"message": "empty"})


class CalculateViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="dsm 이용한 간단한 계산",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "geoJson": openapi.Schema(
                    type=openapi.TYPE_OBJECT, description="geoJSON Type"
                )
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
    def calculation(self, request, projectId, mosaicId):
        email = str(request.user)
        mosaic = Mosaics.objects.get(email=email, projectId=projectId, id=mosaicId)
        if mosaic is not None:
            result = calculateByDSM([request.data["geoJson"]], mosaic)
            return Response(result)
        return Response({"message": "empty"})

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="dsm 부피 계산",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "geoJson": openapi.Schema(
                    type=openapi.TYPE_OBJECT, description="geoJSON Type"
                ),
                "minz": openapi.Schema(type=openapi.TYPE_NUMBER, description="바닥면 높이"),
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
        detail=False,
        methods=["post"],
        url_path=r"volume/(?P<projectId>\d+)/(?P<mosaicId>\d+)",
    )
    def volume(self, request, projectId, mosaicId):
        email = str(request.user)
        if request.data["geoJson"]["type"] != "Polygon":
            return Response({"message": "invalid data"}, status=status.HTTP_200_OK)
        mosaic = Mosaics.objects.get(email=email, projectId=projectId, id=mosaicId)
        if mosaic is not None:
            result = calculateVolume(
                [request.data["geoJson"]], mosaic, request.data["minz"]
            )
            return Response(result, status=status.HTTP_200_OK)
        return Response({"message": "empty"}, status=status.HTTP_200_OK)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="dsm high profile",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "geoJson": openapi.Schema(
                    type=openapi.TYPE_OBJECT, description="geoJSON Type"
                ),
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
        detail=False,
        methods=["post"],
        url_path=r"elevation/(?P<projectId>\d+)/(?P<mosaicId>\d+)",
    )
    def elevation(self, request, projectId, mosaicId):
        email = str(request.user)
        if request.data["geoJson"]["type"] != "LineString":
            return Response({"message": "invalid data"}, status=status.HTTP_200_OK)
        mosaic = Mosaics.objects.get(email=email, projectId=projectId, id=mosaicId)
        if mosaic is not None:
            result = getHighProfile([request.data["geoJson"]], mosaic)
            return Response(result)
        return Response({"message": "empty"})


class CalculateVolumeViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="dsm 부피 계산",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "geoJson": openapi.Schema(
                    type=openapi.TYPE_OBJECT, description="geoJSON Type"
                ),
                "minz": openapi.Schema(type=openapi.TYPE_NUMBER, description="바닥면 높이"),
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
    def volume(self, request, projectId, mosaicId):
        email = str(request.user)
        mosaic = Mosaics.objects.get(email=email, projectId=projectId, id=mosaicId)
        if mosaic is not None:
            result = calculateVolume(
                [request.data["geoJson"]], mosaic, request.data["minz"]
            )
            return Response(result)
        return Response({"message": "empty"})


# =========================CALCULATE3D================================
