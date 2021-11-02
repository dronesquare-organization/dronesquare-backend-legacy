# -*- coding: utf-8 -*-
import base64
import os
import shutil
import zipfile
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import QueryDict, HttpResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from users.models import Users
from .models import Projects, DataProcess, DataProcessFile, AnomalyTypes, AnomalyDegree
from .serializers import (
        ProjectFormSerializer, 
        ProjectsSerializer, 
        ProjectUpdateSerializer, 
        DataProcessInputSerializer,
        DataProcessReadSerializer, 
        ProjectJoinDataProcessSerializer,
        DataProcessSaveSerializer,
    )

# Create your views here.
# =========================PROJECTS===================================
class NewProjectsViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    @swagger_auto_schema(operation_description="프로젝트 생성",
                        request_body=ProjectFormSerializer,
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING)])
    def create(self, request):
        email = str(request.user)
        request.data["email"] = email

        serializer = ProjectsSerializer(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            project = Projects.objects.get(id=serializer.data["id"], email=email)
            users = Users.objects.get(email=email)
            AnomalyTypes.objects.create(projectId = project, email=users)
            AnomalyDegree.objects.create(projectId = project, email=users)
        
            return Response(serializer.data, status=200)
        return Response({"message": "fail"}, status=400)


class ProjectsListViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    @swagger_auto_schema(operation_description="프로젝트 목록",
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING)])
    def list(self, request):
        projects = Projects.objects.filter(email=str(request.user))
        serializer = ProjectsSerializer(projects, many=True)
        return Response(serializer.data)


class ProjectsDetailViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    @swagger_auto_schema(operation_description="프로젝트 세부사항",
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING)])
    def retrieve(self, request, pk=None):
        project = Projects.objects.filter(id=pk, email=str(request.user))

        if len(project) != 0:
            serializer = ProjectJoinDataProcessSerializer(instance = project[0])
            return Response(serializer.data)
        return Response({"message":"empty"})

    @transaction.atomic
    @swagger_auto_schema(operation_description="프로젝트 제거",
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING)])
    def destroy(self, request, pk):
        email = str(request.user)
        project = Projects.objects.get(id=pk, email=email)
        if project is not None:
            path = settings.MEDIA_ROOT + "/{email}/projects/{projectId}".format(email=email, projectId=pk)
            if os.path.exists(path):
                shutil.rmtree(path)
            project.delete()
        return Response({"message": "success"})

    @transaction.atomic
    @swagger_auto_schema(operation_description="프로젝트 변경",
                        request_body=ProjectUpdateSerializer,
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING)])
    def partial_update(self, request, pk):
        email = str(request.user)
        query_set = Projects.objects.all()
        project = get_object_or_404(query_set, id=pk, email=email)
        request.data["id"] = pk
        request.data["email"] = email
        serializer = ProjectUpdateSerializer(project, data=request.data, context={"request": request})
        serializer.is_valid()
        serializer.save()
        updatedProject = Projects.objects.get(id=pk, email=email)
        result = ProjectsSerializer(updatedProject)
        return Response(result.data)
# =========================PROJECTS===================================

# =========================DATA-PROCESS===============================
class DataProcessViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    @swagger_auto_schema(operation_description="데이터 프로세스 신청",
                        request_body=DataProcessInputSerializer,
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING)])
    def create(self, request):
        email = str(request.user)
        request.data["email"] = email
        serailzer = DataProcessSaveSerializer(data=request.data, context={"request": request})
        
        if serailzer.is_valid(raise_exception=True):
            serailzer.save()
            return Response(serailzer.data, status=200)
        return Response({"message":"fail"}, status=400)
    
    @transaction.atomic
    @swagger_auto_schema(tags=["data-process"],
                        operation_description="데이터 프로세스 조회",
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING),
                            openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)")                                            
    def info(self, request, projectId):
        email = str(request.user)
        dataprocess = DataProcess.objects.filter(projectId=projectId, email=email)
        if len(dataprocess) != 0:
            serialzer = DataProcessReadSerializer(instance=dataprocess[0])
            return Response(serialzer.data)
        return Response({"message":"empty"})
# =========================DATA-PROCESS===============================


# =========================DATA-PROCESS-FILE==========================
class DataProcessFileViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    @swagger_auto_schema(tags=["data-process-file"],
                        operation_description="데이터 프로세스 파일 타입 목록",
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING),
                            openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)")
    def info(self, request, projectId):
        email = str(request.user)
        try:
            project = Projects.objects.get(id=projectId, email=email)
            dataprocessId = project.dataprocess.id
            processFiles = DataProcessFile.objects.filter(email=email, dataprocessId=dataprocessId).values_list("fileType", flat=True).order_by("fileType").distinct("fileType")
            return Response(processFiles)
        except Projects.DoesNotExist:
            return Response({"message":"empty"})
        except Projects.dataprocess.RelatedObjectDoesNotExist:
            return Response({"message":"empty"})
    
    @transaction.atomic
    @swagger_auto_schema(tags=["data-process-file"],
                        operation_description="데이터 프로세스 파일 다운로드(추후 작업 예정)",
                        request_body=openapi.Schema(
                            type=openapi.TYPE_OBJECT, 
                            properties={
                                'dataprocessId': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'fileType': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)
                                    , description='array'),
                            }
                        ),
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING)])
    def create(self, request):
        email = str(request.user)
        processFile = DataProcessFile.objects.filter(fileType__in=request.data["fileType"], email=email, dataprocessId=request.data["dataprocessId"])
        if len(processFile) != 0:
            # with zipfile.ZipFile('data/temp/new_comp.zip', 'a') as existing_zip:
            #     existing_zip.write('data/temp/test4.txt', arcname='test4.txt')
            return Response({"message":"after update"})
        return Response({"message":"empty"})
# =========================DATA-PROCESS-FILE==========================

# =========================ANOMALY-TYPE==============================
class AnomalyTypesViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


    @transaction.atomic()
    @swagger_auto_schema(method="get",
                        operation_description="이슈 타입 조회",
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING),
                            openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                            type=openapi.TYPE_INTEGER)])
    @transaction.atomic()                                            
    @swagger_auto_schema(method="patch",
                        operation_description="이슈 타입 변경",
                        request_body=openapi.Schema(
                            type=openapi.TYPE_OBJECT, 
                            properties={
                                'types': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='array'),
                            }
                        ),
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING),
                            openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                            type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["patch", "get"], url_path=r"(?P<projectId>\d+)")
    def anomalyType(self, request, projectId):
        email = str(request.user)
        anomalyTypes = AnomalyTypes.objects.filter(email=email, projectId=projectId)
        if anomalyTypes.exists():
            if request.method == "PATCH":
                anomalyTypes.update(types=request.data["types"])
                return Response({"data":anomalyTypes[0].types})
            else:
                return Response({"data":anomalyTypes[0].types})
        return Response({"message":"empty"})


    

        

# =========================ANOMALY-TYPE==============================

# =========================ANOMALY-DEGREE============================
class AnomalyDegreeViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(method="get",
                        operation_description="이슈 정도 조회",
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING),
                            openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                            type=openapi.TYPE_INTEGER)])
    @transaction.atomic()
    @swagger_auto_schema(method="patch",
                        operation_description="이슈 정도 변경",
                        request_body=openapi.Schema(
                            type=openapi.TYPE_OBJECT, 
                            properties={
                                'types': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='array'),
                            }
                        ),
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING),
                            openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                            type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["patch", "get"], url_path=r"(?P<projectId>\d+)")
    def anomalyDegree(self, request, projectId):
        email = str(request.user)
        anomalyDegree = AnomalyDegree.objects.filter(email=email, projectId=projectId)
        if anomalyDegree.exists():
            if request.method == "PATCH":
                anomalyDegree.update(types=request.data["types"])
                return Response({"data":anomalyDegree[0].types})
            else:
                return Response({"data":anomalyDegree[0].types})
        return Response({"message":"empty"})
# =========================ANOMALY-DEGREE============================