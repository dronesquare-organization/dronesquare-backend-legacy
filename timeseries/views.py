# Django Apis
from django.db import transaction
from django.db.models import Count

# Project Apps
from projects.models import Projects
from .models import TimeSeries, TimeSeriesRelation
from .serializers import (
    TimeSeriesInputSerializer,
    TimeSeriesRelationByProjectIdSerializer,
    TimeSeriesRelationInputSerializer,
    TimeSeriesRelationSerializer,
    TimeSeriesSerializer,
)

# Third Party Packages
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

# =========================TIMESERIES=================================
class TimeSeriesViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="시계열 그룹 생성",
        request_body=TimeSeriesInputSerializer,
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

        serializer = TimeSeriesSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "fail"}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="시계열 그룹 이름 변경",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="시계열 그룹 이름"
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
    def partial_update(self, request, pk):
        email = str(request.user)
        timeseries = TimeSeries.objects.filter(email=email, id=pk)
        if timeseries is not None:
            timeseries.update(name=request.data["name"])
            return Response({"message": "update success"})
        return Response({"message": "not Exist"}, status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="시계열 그룹 조회",
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
        timeseries = TimeSeries.objects.filter(email=str(request.user))
        serializer = TimeSeriesSerializer(timeseries, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="시계열 그룹 삭제",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "idSet": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description="array",
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
    @action(detail=False, methods=["patch"])
    def group(self, request):
        email = str(request.user)
        idSet = request.data["idSet"]
        if len(idSet) == 0:
            return Response({"message": "empty"})
        timeseries = TimeSeries.objects.filter(email=email, id__in=idSet)
        if timeseries.exists():
            timeseries.delete()
            return Response({"message": "success"})
        else:
            return Response({"message": "empty"})
        return Response({"message": "fail"})


class TimeSeriesFindByProjectViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        tags=["timeseries-project"],
        operation_description="프로젝트 아이디로 시계열 그룹 조회",
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
    def findByProjectId(self, request, projectId):
        email = str(request.user)
        timeseries = TimeSeries.objects.filter(relation__projectInfo=projectId)
        if len(timeseries) == 0:
            return Response({"message": "empty"})
        serializer = TimeSeriesRelationByProjectIdSerializer(
            instance=timeseries, many=True
        )
        return Response(serializer.data)


class TimeSeriesRelationViewSet(viewsets.ViewSet):
    @transaction.atomic
    @swagger_auto_schema(
        operation_description="시계열 관계 생성",
        request_body=TimeSeriesRelationInputSerializer,
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
        relation = TimeSeriesRelation.objects.filter(
            timeseriesId=request.data["timeseriesId"],
            projectInfo=request.data["projectInfo"],
        ).aggregate(count_of_relation=Count("projectInfo"))

        if relation["count_of_relation"] != 0:
            return Response({"message": "Already exist"}, status=status.HTTP_200_OK)
        serializer = TimeSeriesRelationSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            relationInfo = TimeSeriesRelation.objects.filter(
                projectInfo=request.data["projectInfo"]
            ).aggregate(count_of_relation=Count("projectInfo"))
            project = Projects.objects.filter(id=request.data["projectInfo"])
            project.update(timeSeriesCnt=relationInfo["count_of_relation"])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="시계열 관계 삭제",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "idSet": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "groupId": openapi.Schema(
                                type=openapi.TYPE_INTEGER, description="object"
                            ),
                            "relationIdSet": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Items(type=openapi.TYPE_INTEGER),
                                description="array",
                            ),
                        },
                    ),
                    description="array",
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
    @action(detail=False, methods=["patch"])
    def group(self, request):
        email = str(request.user)
        idSet = request.data["idSet"]
        if len(idSet) == 0:
            return Response({"message": "invalid"})
        for Set in idSet:
            relation = TimeSeriesRelation.objects.filter(
                id__in=Set["relationIdSet"], email=email, timeseriesId=Set["groupId"]
            )
            if relation.exists():
                relation.delete()
        return Response({"message": "success"})


# =========================TIMESERIES=================================
