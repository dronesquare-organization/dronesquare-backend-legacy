import mimetypes
import os
import shutil
from wsgiref.util import FileWrapper
import boto3
from django.conf import settings
from django.core.files.base import File
from django.db import transaction
from django.db.models import Count, Sum
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from PIL import Image
from projects.models import Projects
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import (FileUploadParser, FormParser,
                                    MultiPartParser)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models import Users
from utils.DuplicateName import createFileName

from .models import GCP, Etc2D3DLayers, EtcDocs, EtcImgs, NestedLayers, Video
from .serializers import (Etc2D3DLayersSerializer, EtcDocsSerializer,
                          EtcImgsSerializer, GCPSerializer,
                          NestedLayersSerializer, VideoListUploadSerializer,
                          VideoSerializer)
from utils.ImgUploadSave import delfolder_exist, create_tmpfolder, path_settings_gcp, path_settings
from io import BytesIO

# Create your views here.

# =========================VIDEO======================================
class VideoViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic()
    @swagger_auto_schema(operation_description="비디오 파일 업로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter('projectId', in_= openapi.IN_FORM, description="projectId",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter('files', in_=openapi.IN_FORM, description="file list",
                                               type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_FILE)),
                             ])
    def create(self, request):
        accept = ["mp4"]
        email = str(request.user)
        projectId = request.data["projectId"]
        fileList = request.FILES.getlist("files")
        if type(request.data) != dict:
            file = fileList[0]

            tmppath = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/etcTempVideo".format(email=str(email),
                                                                                                    projectId=
                                                                                                    request.data[
                                                                                                        "projectId"])
            path = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/etcVideo".format(email=str(email),
                                                                                                    projectId=
                                                                                                    request.data[
                                                                                                        "projectId"])

            # cr_path = path_settings(email, projectId)
            #
            # paths_name = ['etcTempVideo','etcVideo']
            # tmppath, path =


            if request.data['is_Start']== "true":
                if os.path.exists(tmppath):
                    shutil.rmtree(tmppath)

            if not os.path.exists(tmppath):
                os.makedirs(tmppath)
            tmpSaveName = "".join(file.name.split(".part")[0].split(" "))
            destination = open(tmppath + "/" + tmpSaveName, "ab+")

            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()

            if request.data['is_last'] == "true" and request.data['allFileLength'] == request.data['index']:
                onlyfiles = [f for f in os.listdir(tmppath) if os.path.isfile(os.path.join(tmppath, f))]
                projects = Projects.objects.get(id=request.data["projectId"])
                users = Users.objects.get(email=email)
                fail = []
                for f in onlyfiles:
                    if str(f).split(".")[-1].lower() in accept:
                        fileName = createFileName(path+"/"+"".join(f.split(" ")), f)
                        t = open(tmppath+"/"+f, 'rb')
                        size = os.path.getsize(tmppath+"/"+f)
                        ext = mimetypes.guess_type(f)[0]
                        video = Video.objects.create(name=fileName, projectId = projects, size=size, ext=ext, fileDir=File(t), email=users)
                        t.close()
                    else:
                        fail.append(f)
                result = Video.objects.filter(email=email, projectId=request.data["projectId"]).aggregate(sum_of_size=Sum("size"))
                if result["sum_of_size"] is not None:
                    projects.videoVolume =  result["sum_of_size"]
                    projects.save()
                videoList = Video.objects.filter(projectId = projects.id, email=users.email).order_by("-uploadDate")
                serializer = VideoSerializer(videoList, many=True)
                if os.path.exists(tmppath):
                    shutil.rmtree(tmppath)
                return Response({"fail":fail, "etcData":serializer.data})
        return Response({"message":"continue"})

class VideoDeleteViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="비디오 삭제",
                         request_body=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'idSet': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='array'),
                                }
                            ),
                            manual_parameters=[
                                openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                                type=openapi.TYPE_STRING),
                                openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                                type=openapi.TYPE_INTEGER)]
                        )
    @action(detail=False, methods=["patch"], url_path=r"(?P<projectId>\d+)")
    def video(self, request, projectId):
        email = str(request.user)
        idSet = request.data["idSet"]
        videos = Video.objects.filter(projectId = projectId, email = email, id__in=idSet)
        if videos.exists():
            for video in videos:
                path = settings.MEDIA_ROOT +"/"+str(video.fileDir)
                os.remove(path)
            videos.delete()
        else:
            return Response({"message":"file is not exist"})
        result = Video.objects.filter(email=email, projectId=projectId).aggregate(sum_of_size=Sum("size"))
        if result["sum_of_size"] is not None:
            project = Projects.objects.filter(email=email, id=projectId)
            if project.exists():
                project.update(videoVolume= result["sum_of_size"])
        return Response({"message":"success"})


class VideoListViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="비디오 리스트 조회",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)", url_name="video")
    def videos(self, request, projectId):
        email = str(request.user)
        request.data["email"]=email
        videoList = Video.objects.filter(projectId=projectId, email=email)
        serializer = VideoSerializer(videoList, many=True)
        return Response(serializer.data)


class VideoDownloadViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="비디오 다운로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter("id", openapi.IN_PATH, description="ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)/(?P<id>\d+)", url_name="video")
    def video(self, request, projectId, id):
        email = str(request.user)
        request.data["email"]=email
        video = Video.objects.filter(projectId = projectId, email = email, id = id)
        if video.exists():
            video = video.first()
            
            file_path = "media/"+str(video.fileDir)
            print(file_path)
            try:
                s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                bucket='droneplatform'
                obj = s3_client.get_object(Bucket=bucket, Key=file_path)
                response = HttpResponse(FileWrapper(BytesIO(obj['Body'].read())), content_type=video.ext)
                response["Content-Length"] = video.size
                response['Content-Disposition'] = 'inline; filename=%s' % video.name
                return response
            except Exception as e:
                print(e, flush=True)
                return Response({"message":"not exist"})
                
        return Response({"message":"not exist"})


# =========================VIDEO======================================

# =========================ETCIMG======================================
class EtcImgsViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic()
    @swagger_auto_schema(operation_description="기타 이미지 파일 업로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter('projectId', in_= openapi.IN_FORM, description="projectId",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter('files', in_=openapi.IN_FORM, description="file list",
                                               type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_FILE)),
                             ])

    def create(self, request):
        accept = ["jpg", "png", "jpeg"]
        email = str(request.user)
        fileList = request.FILES.getlist("files")
        if type(request.data) != dict:
            file = fileList[0]

            tmppath = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/etcTempImg".format(email=str(email),
                                                                                                    projectId=
                                                                                                    request.data[
                                                                                                        "projectId"])
            path = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/etcImg".format(email=str(email),
                                                                                                    projectId=
                                                                                                    request.data[
                                                                                                        "projectId"])
            if request.data['is_Start']== "true":
                if os.path.exists(tmppath):
                    shutil.rmtree(tmppath)

            if not os.path.exists(tmppath):
                os.makedirs(tmppath)
            tmpSaveName = "".join(file.name.split(".part")[0].split(" "))
            destination = open(tmppath + "/" + tmpSaveName, "ab+")

            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()

            if request.data['is_last'] == "true" and request.data['allFileLength'] == request.data['index']:
                onlyfiles = [f for f in os.listdir(tmppath) if os.path.isfile(os.path.join(tmppath, f))]
                projects = Projects.objects.get(id=request.data["projectId"])
                users = Users.objects.get(email=email)
                fail = []
                for f in onlyfiles:
                    if str(f).split(".")[-1].lower() in accept:
                        file = Image.open(tmppath+"/"+f)
                        fileName = createFileName(path+"/"+"".join(f.split(" ")), f)
                        t = open(tmppath+"/"+f, 'rb')
                        size = os.path.getsize(tmppath+"/"+f)
                        ext = "image/"+str(f).split(".")[-1].lower()
                        etcImg = EtcImgs.objects.create(name=fileName, projectId = projects, width=file.width, height=file.height, size=size, ext=ext, fileDir=File(t), email=users)
                        file.close()
                        t.close()
                        # TO-DO : 용량 계산하기
                    else:
                        fail.append(f)
                etcImgList = EtcImgs.objects.filter(projectId = projects.id, email=users.email).order_by("-uploadDate")
                serializer = EtcImgsSerializer(etcImgList, many=True)
                if os.path.exists(tmppath):
                    shutil.rmtree(tmppath)
                return Response({"fail":fail, "etcData":serializer.data})
        return Response({"message":"continue"})


class EtcImgsDeleteViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="기타 이미지 파일 삭제",
                            request_body=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'idSet': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='array'),
                                }
                            ),
                            manual_parameters=[
                                openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                                type=openapi.TYPE_STRING),
                                openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                                type=openapi.TYPE_INTEGER)]
                        )
    @action(detail=False, methods=["patch"], url_path=r"(?P<projectId>\d+)")
    def deleteEtcImgs(self, request, projectId):
        email = str(request.user)
        idSet = request.data["idSet"]
        etcImgs = EtcImgs.objects.filter(projectId = projectId, email = email, id__in=idSet)
        if etcImgs.exists():
            for ei in etcImgs:
                path = settings.MEDIA_ROOT +"/"+str(ei.fileDir)
                os.remove(path)
            etcImgs.delete()
            # TO-DO : 기타 이미지 파일 삭제 시 용량 업데이트
        else:
            return Response({"message":"file is not exist"})
        return Response({"message":"success"})


class EtcImgsListViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="기타 이미지 파일 리스트 조회",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)", url_name="video")
    def getListetcImgs(self, request, projectId):
        email = str(request.user)
        request.data["email"]=email
        EtcImgsList = EtcImgs.objects.filter(projectId=projectId, email=email)
        serializer = EtcImgsSerializer(EtcImgsList, many=True)

        return Response(serializer.data)


class EtcImgsDownloadViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="기타 이미지 파일 다운로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter("id", openapi.IN_PATH, description="ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)/(?P<id>\d+)")
    def etcImgs(self, request, projectId, id):
        email = str(request.user)
        request.data["email"]=email
        etcImgs = EtcImgs.objects.filter(projectId = projectId, email = email, id = id)
        if etcImgs.exists():
            etcImg = etcImgs.first()
            file_path = "media/"+str(etcImg.fileDir)
            try:
                s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                bucket='droneplatform'
                obj = s3_client.get_object(Bucket=bucket, Key=file_path)
                response = HttpResponse(FileWrapper(BytesIO(obj['Body'].read())), content_type=etcImg.ext)
                response["Content-Length"] = etcImg.size
                response['Content-Disposition'] = 'inline; filename=%s' % etcImg.name
                return response
            except Exception as e:
                print(e, flush=True)
                return Response({"message":"not exist"})
        return Response({"message":"not exist"})
# =========================ETCIMG======================================

# =========================ETCDOC======================================
class EtcDocsViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic()
    @swagger_auto_schema(operation_description="기타 문서 파일 업로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter('projectId', in_= openapi.IN_FORM, description="projectId",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter('files', in_=openapi.IN_FORM, description="file list",
                                               type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_FILE)),
                             ])

    def create(self, request):
        accept = ["hwp", "xlsx", "pdf", "ppt", "pptx"]
        email = str(request.user)
        fileList = request.FILES.getlist("files")
        if type(request.data) != dict:
            file = fileList[0]

            tmppath = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/etcTempDoc".format(email=str(email),
                                                                                                    projectId=
                                                                                                    request.data[
                                                                                                        "projectId"])
            path = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/etcDoc".format(email=str(email),
                                                                                                    projectId=
                                                                                                    request.data[
                                                                                                        "projectId"])
            if request.data['is_Start']== "true":
                if os.path.exists(tmppath):
                    shutil.rmtree(tmppath)

            if not os.path.exists(tmppath):
                os.makedirs(tmppath)
            tmpSaveName = "".join(file.name.split(".part")[0].split(" "))
            destination = open(tmppath + "/" + tmpSaveName, "ab+")

            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()

            if request.data['is_last'] == "true" and request.data['allFileLength'] == request.data['index']:
                onlyfiles = [f for f in os.listdir(tmppath) if os.path.isfile(os.path.join(tmppath, f))]
                projects = Projects.objects.get(id=request.data["projectId"])
                users = Users.objects.get(email=email)
                fail=[]
                for f in onlyfiles:
                    if str(f).split(".")[-1].lower() in accept:
                        fileName = createFileName(path+"/"+"".join(f.split(" ")), f)
                        t = open(tmppath+"/"+f, 'rb')
                        size = os.path.getsize(tmppath+"/"+f)
                        ext = mimetypes.guess_type(f)[0]
                        etcDoc = EtcDocs.objects.create(name=fileName, projectId = projects, size=size, ext=ext, fileDir=File(t), email=users)
                        file.close()
                        t.close()
                        # TO-DO : 용량 계산하기
                    else:
                        fail.append(f)
                etcDocList = EtcDocs.objects.filter(projectId = projects.id, email=users.email).order_by("-uploadDate")
                serializer = EtcDocsSerializer(etcDocList, many=True)
                if os.path.exists(tmppath):
                    shutil.rmtree(tmppath)
                return Response({"fail":fail, "etcData":serializer.data})
        return Response({"message":"continue"})


class EtcDocsDeleteViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="기타 문서 파일 삭제",
                            request_body=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'idSet': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='array'),
                                }
                            ),
                            manual_parameters=[
                                openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                                type=openapi.TYPE_STRING),
                                openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                                type=openapi.TYPE_INTEGER)]
                        )
    @action(detail=False, methods=["patch"], url_path=r"(?P<projectId>\d+)")
    def deleteEtcDocs(self, request, projectId):
        email = str(request.user)
        idSet = request.data["idSet"]
        etcDocs = EtcDocs.objects.filter(projectId = projectId, email = email, id__in=idSet)
        if etcDocs.exists():
            for ei in etcDocs:
                path = settings.MEDIA_ROOT +"/"+str(ei.fileDir)
                os.remove(path)
            etcDocs.delete()
            # TO-DO : 기타 문서 파일 삭제 시 용량 업데이트
        else:
            return Response({"message":"file is not exist"})
        return Response({"message":"success"})


class EtcDocsListViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="기타 문서 파일 리스트 조회",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)", url_name="video")
    def getEtcDocsList(self, request, projectId):
        email = str(request.user)
        request.data["email"]=email
        EtcDocsList = EtcDocs.objects.filter(projectId=projectId, email=email)
        serializer = EtcDocsSerializer(EtcDocsList, many=True)

        return Response(serializer.data)


class EtcDocsDownloadViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="기타 문서 파일 다운로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter("id", openapi.IN_PATH, description="ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)/(?P<id>\d+)")
    def etcDocs(self, request, projectId, id):
        email = str(request.user)
        request.data["email"]=email
        etcDocs = EtcDocs.objects.filter(projectId = projectId, email = email, id = id)


        
        if etcDocs.exists():
            etcDoc = etcDocs.first()
            file_path = "media/"+str(etcDoc.fileDir)
            try:
                s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                bucket='droneplatform'
                obj = s3_client.get_object(Bucket=bucket, Key=file_path)
                response = HttpResponse(FileWrapper(BytesIO(obj['Body'].read())), content_type=etcDoc.ext)
                response["Content-Length"] = etcDoc.size
                response['Content-Disposition'] = 'inline; filename=%s' % etcDoc.name
                return response
            except Exception as e:
                print(e, flush=True)
                return Response({"message":"not exist"})
        return Response({"message":"not exist"})
# =========================ETCDOC======================================

# =========================NESTEDLAYER=================================
class NestedLayersViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic()
    @swagger_auto_schema(operation_description="레이어 중첩 파일 업로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter('projectId', in_= openapi.IN_FORM, description="projectId",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter('files', in_=openapi.IN_FORM, description="file list",
                                               type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_FILE)),
                             ])

    def create(self, request):
        accept = ["png", "jpg", "dxf", "tif", "twf", "prj"]
        email = str(request.user)
        projectId = request.data['projectId']
        fileList = request.FILES.getlist("files")
        if type(request.data) != dict:
            file = fileList[0]

            cr_path = path_settings(email, projectId)

            tmp_paths_name = ['etcTempNestedLayer', 'nestedLayer']
            tmppath, path = list(map(cr_path, tmp_paths_name))

            if request.data['is_Start']== "true":
                if os.path.exists(tmppath):
                    shutil.rmtree(tmppath)

            if not os.path.exists(tmppath):
                os.makedirs(tmppath)
            tmpSaveName = "".join(file.name.split(".part")[0].split(" "))
            destination = open(tmppath + "/" + tmpSaveName, "ab+")

            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()

            if request.data['is_last'] == "true" and request.data['allFileLength'] == request.data['index']:
                onlyfiles = [f for f in os.listdir(tmppath) if os.path.isfile(os.path.join(tmppath, f))]
                projects = Projects.objects.get(id=request.data["projectId"])
                users = Users.objects.get(email=email)
                fail=[]
                for f in onlyfiles:
                    if str(f).split(".")[-1].lower() in accept:
                        fileName = createFileName(path+"/"+"".join(f.split(" ")), f)
                        t = open(tmppath+"/"+f, 'rb')
                        size = os.path.getsize(tmppath+"/"+f)
                        ext = mimetypes.guess_type(f)[0]
                        layer = NestedLayers.objects.create(name=fileName, projectId = projects, size=size, ext=ext, fileDir=File(t, name=fileName), email=users)
                        file.close()
                        t.close()
                        # TO-DO : 용량 계산하기
                    else:
                        fail.append(f)
                nestedLayerList = NestedLayers.objects.filter(projectId = projects.id, email=users.email).order_by("-uploadDate")
                serializer = NestedLayersSerializer(nestedLayerList, many=True)
                if os.path.exists(tmppath):
                    shutil.rmtree(tmppath)
                return Response({"fail":fail, "etcData":serializer.data})
        return Response({"message":"continue"})


class NestedLayersUpdateViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="레이어 중첩 파일, 레이어 중첩 리스트 추가",
                        request_body=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'body': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                        'id':openapi.Schema(type=openapi.TYPE_INTEGER, description='id'),
                                        'coordSystem':openapi.Schema(type=openapi.TYPE_STRING,  description='coordSystem')
                                    }), description='array'),
                            }
                        ),
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter('projectId', in_= openapi.IN_PATH, description="projectId",
                                               type=openapi.TYPE_INTEGER),
                             ])
    @action(detail=False, methods=["patch"], url_path=r"(?P<projectId>\d+)")
    def enroll(self, request, projectId):
        print(request.data)
        email = str(request.user)
        NestedLayers.objects.filter(email=email, projectId=projectId).update(isEnroll=False)
        for data in request.data:
            nestedLayer = NestedLayers.objects.filter(email=email, projectId=projectId, id=data["id"]).update(isEnroll=True, coordSystem=data["coordSystem"])
        NestedLayerList = NestedLayers.objects.filter(projectId=projectId, email=email)
        serializer = NestedLayersSerializer(NestedLayerList, many=True)

        return Response(serializer.data)



class NestedLayersDeleteViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="레이어 중첩 파일 삭제",
                            request_body=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'idSet': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='array'),
                                }
                            ),
                            manual_parameters=[
                                openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                                type=openapi.TYPE_STRING),
                                openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                                type=openapi.TYPE_INTEGER)]
                        )
    @action(detail=False, methods=["patch"], url_path=r"(?P<projectId>\d+)")
    def deleteNestedLayer(self, request, projectId):
        email = str(request.user)
        idSet = request.data["idSet"]
        nestedLayer = NestedLayers.objects.filter(projectId = projectId, email = email, id__in=idSet)
        if nestedLayer.exists():
            for ei in nestedLayer:
                path = settings.MEDIA_ROOT +"/"+str(ei.fileDir)
                os.remove(path)
            nestedLayer.delete()
            # TO-DO : 기타 문서 파일 삭제 시 용량 업데이트
        else:
            return Response({"message":"file is not exist"})
        return Response({"message":"success"})


class NestedLayersListViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="레이어 중첩 파일 리스트 조회",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)", url_name="video")
    def getNestedLayersList(self, request, projectId):
        email = str(request.user)
        request.data["email"]=email
        NestedLayerList = NestedLayers.objects.filter(projectId=projectId, email=email)
        serializer = NestedLayersSerializer(NestedLayerList, many=True)

        return Response(serializer.data)


class NestedLayersDownloadViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="레이어 중첩 파일 다운로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter("id", openapi.IN_PATH, description="ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)/(?P<id>\d+)")
    def NestedLayers(self, request, projectId, id):
        email = str(request.user)
        request.data["email"]=email
        nestedLayers = NestedLayers.objects.filter(projectId = projectId, email = email, id = id)
        if nestedLayers.exists():
            nestedLayer = nestedLayers.first()
            file_path = "media/"+str(nestedLayer.fileDir)
            try:
                s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
                bucket='droneplatform'
                obj = s3_client.get_object(Bucket=bucket, Key=file_path)
                response = HttpResponse(FileWrapper(BytesIO(obj['Body'].read())), content_type=nestedLayer.ext)
                response["Content-Length"] = nestedLayer.size
                response['Content-Disposition'] = 'inline; filename=%s' % nestedLayer.name
                return response
            except Exception as e:
                print(e, flush=True)
                return Response({"message":"not exist"})
        return Response({"message":"not exist"})
# =========================NESTEDLAYER=================================

# =========================ETC2D3DLAYER================================
class Etc2D3DLayersViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic()
    @swagger_auto_schema(operation_description="기타 2D3D 레이어 파일 업로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter('projectId', in_= openapi.IN_FORM, description="projectId",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter('files', in_=openapi.IN_FORM, description="file list",
                                               type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_FILE)),
                             ])

    def create(self, request):
        accept = ["las", "mtl", "jpg", "obj", "fbx", "tif", "twf", "prj"]
        email = str(request.user)
        fileList = request.FILES.getlist("files")
        if type(request.data) != dict:
            file = fileList[0]
            tmppath = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/etcTemp2D3DLayer".format(email=str(email),
                                                                                                    projectId=
                                                                                                    request.data[
                                                                                                        "projectId"])
            path = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/etc2D3DLayer".format(email=str(email),
                                                                                                    projectId=
                                                                                                    request.data[
                                                                                                        "projectId"])
            if request.data['is_Start']== "true":
                if os.path.exists(tmppath):
                    shutil.rmtree(tmppath)

            if not os.path.exists(tmppath):
                os.makedirs(tmppath)
            tmpSaveName = "".join(file.name.split(".part")[0].split(" "))
            destination = open(tmppath + "/" + tmpSaveName, "ab+")

            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()

            if request.data['is_last'] == "true" and request.data['allFileLength'] == request.data['index']:
                onlyfiles = [f for f in os.listdir(tmppath) if os.path.isfile(os.path.join(tmppath, f))]
                projects = Projects.objects.get(id=request.data["projectId"])
                users = Users.objects.get(email=email)
                fail=[]
                for f in onlyfiles:
                    if str(f).split(".")[-1].lower() in accept:
                        fileName = createFileName(path+"/"+"".join(f.split(" ")), f)
                        t = open(tmppath+"/"+f, 'rb')
                        size = os.path.getsize(tmppath+"/"+f)
                        ext = mimetypes.guess_type(f)[0]
                        layer = Etc2D3DLayers.objects.create(name=fileName, projectId = projects, size=size, ext=ext, fileDir=File(t), email=users)
                        file.close()
                        t.close()
                        # TO-DO : 용량 계산하기
                    else:
                        fail.append(f)
                etc2D3DLayersList = Etc2D3DLayers.objects.filter(projectId = projects.id, email=users.email).order_by("-uploadDate")
                serializer = Etc2D3DLayersSerializer(etc2D3DLayersList, many=True)
                if os.path.exists(tmppath):
                    shutil.rmtree(tmppath)
                return Response({"fail":fail, "etcData":serializer.data})
        return Response({"message":"continue"})


class Etc2D3DLayersDeleteViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="기타 2D3D 레이어 파일 삭제",
                            request_body=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'idSet': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='array'),
                                }
                            ),
                            manual_parameters=[
                                openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                                type=openapi.TYPE_STRING),
                                openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                                type=openapi.TYPE_INTEGER)]
                        )
    @action(detail=False, methods=["patch"], url_path=r"(?P<projectId>\d+)")
    def deleteEtc2D3DLayer(self, request, projectId):
        email = str(request.user)
        idSet = request.data["idSet"]
        etc2D3DLayers = Etc2D3DLayers.objects.filter(projectId = projectId, email = email, id__in=idSet)
        if etc2D3DLayers.exists():
            for ei in etc2D3DLayers:
                path = settings.MEDIA_ROOT +"/"+str(ei.fileDir)
                os.remove(path)
            etc2D3DLayers.delete()
            # TO-DO : 기타 문서 파일 삭제 시 용량 업데이트
        else:
            return Response({"message":"file is not exist"})
        return Response({"message":"success"})


class Etc2D3DLayersListViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(operation_description="기타 2D3D 레이어 파일 리스트 조회",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)", url_name="video")
    def getEtc2D3DLayersList(self, request, projectId):
        email = str(request.user)
        request.data["email"]=email
        Etc2D3DLayerList = Etc2D3DLayers.objects.filter(projectId=projectId, email=email)
        serializer = Etc2D3DLayersSerializer(Etc2D3DLayerList, many=True)

        return Response(serializer.data)


class Etc2D3DLayersDownloadViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="기타 2D3D 레이어 파일 다운로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter("id", openapi.IN_PATH, description="ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)/(?P<id>\d+)")
    def Etc2D3DLayers(self, request, projectId, id):
        email = str(request.user)
        request.data["email"]=email
        etc2D3DLayers = Etc2D3DLayers.objects.filter(projectId = projectId, email = email, id = id)
        if etc2D3DLayers.exists():
            etc2D3DLayer = etc2D3DLayers.first()
            file_path = settings.MEDIA_ROOT + "/"+str(etc2D3DLayer.fileDir)
            if os.path.exists(file_path):
                doc = open(file_path, 'rb')
                response = HttpResponse(FileWrapper(doc), content_type=etc2D3DLayers.ext)
                response["Content-Length"] = etc2D3DLayers.size
                response['Content-Disposition'] = 'inline; filename=%s' % etc2D3DLayers.name
                return response
        return Response({"message":"not exist"})
# =========================ETC2D3DLAYER================================

# =========================GCP=========================================
class GCPViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic()
    @swagger_auto_schema(tags=["GCP"],
                        operation_description="GCP 파일 업로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter('projectId', in_= openapi.IN_FORM, description="projectId",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter('files', in_=openapi.IN_FORM, description="file list",
                                               type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_FILE)),
                             ])

    def create(self, request):
        accept = ["csv", "xlsx", "txt"]
        email = str(request.user)
        projectId = request.data['projectId']
        fileList = request.FILES.getlist("files")
        if type(request.data) != dict:

            file = fileList[0]
            cr_path = path_settings_gcp(email, projectId)
            tmp_paths_name = ['tmppath', 'path']
            tmppath, path = list(map(cr_path, tmp_paths_name))

            if request.data['is_Start']== "true":
                delfolder_exist(tmppath, path)

            create_tmpfolder(email, projectId, 'tmppath')


            tmpSaveName = "".join(file.name.split(".part")[0].split(" "))
            destination = open(tmppath + "/" + tmpSaveName, "ab+")

            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()

            if request.data['is_last'] == "true" and request.data['allFileLength'] == request.data['index']:
                onlyfiles = [f for f in os.listdir(tmppath) if os.path.isfile(os.path.join(tmppath, f))]
                projects = Projects.objects.get(id=request.data["projectId"])
                users = Users.objects.get(email=email)
                fail=[]
                for f in onlyfiles:
                    if str(f).split(".")[-1].lower() in accept:
                        fileName = createFileName(path+"/"+"".join(f.split(" ")), f)
                        t = open(tmppath+"/"+f, 'rb')
                        size = os.path.getsize(tmppath+"/"+f)
                        ext = mimetypes.guess_type(f)[0]
                        gcp = GCP.objects.create(name=fileName, projectId = projects, size=size, ext=ext, fileDir=File(t), email=users)
                        file.close()
                        t.close()
                        # TO-DO : 용량 계산하기
                    else:
                        fail.append(f)
                GCPList = GCP.objects.filter(projectId = projects.id, email=users.email).order_by("-uploadDate")
                serializer = GCPSerializer(GCPList, many=True)

                delfolder_exist('/tmp/{}'.format(email))
                return Response({"fail":fail, "gcpData":serializer.data})
        return Response({"message":"continue"})


class GCPDeleteViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(tags=["GCP"],
                        operation_description="GCP 파일 삭제",
                        request_body=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'idSet': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), description='array'),
                            }
                        ),
                        manual_parameters=[
                            openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                            type=openapi.TYPE_STRING),
                            openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                            type=openapi.TYPE_INTEGER)]
                        )
    @action(detail=False, methods=["patch"], url_path=r"(?P<projectId>\d+)")
    def deleteGCP(self, request, projectId):
        email = str(request.user)
        idSet = request.data["idSet"]
        gcp = GCP.objects.filter(projectId = projectId, email = email, id__in=idSet)
        if gcp.exists():
            for ei in gcp:
                path = settings.MEDIA_ROOT +"/"+str(ei.fileDir)
                os.remove(path)
            gcp.delete()
            # TO-DO : 기타 문서 파일 삭제 시 용량 업데이트
        else:
            return Response({"message":"file is not exist"})
        return Response({"message":"success"})


class GCPListViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    @swagger_auto_schema(tags=["GCP"],
                        operation_description="GCP 파일 리스트 조회",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)", url_name="video")
    def getGCPList(self, request, projectId):
        email = str(request.user)
        request.data["email"]=email
        GCPList = GCP.objects.filter(projectId=projectId, email=email)
        serializer = GCPSerializer(GCPList, many=True)

        return Response(serializer.data)


class GCPDownloadViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["GCP"],
                        operation_description="GCP 파일 다운로드",
                         manual_parameters=[
                             openapi.Parameter("Authorization", openapi.IN_HEADER, description="Authorization",
                                               type=openapi.TYPE_STRING),
                             openapi.Parameter("projectId", openapi.IN_PATH, description="PROJECT ID",
                                               type=openapi.TYPE_INTEGER),
                             openapi.Parameter("id", openapi.IN_PATH, description="ID",
                                               type=openapi.TYPE_INTEGER)])
    @action(detail=False, methods=["get"], url_path=r"(?P<projectId>\d+)/(?P<id>\d+)")
    def GCP(self, request, projectId, id):
        email = str(request.user)
        request.data["email"]=email
        gcp = GCP.objects.filter(projectId = projectId, email = email, id = id)
        if gcp.exists():
            gcp = gcp.first()
            file_path = settings.MEDIA_ROOT + "/"+str(gcp.fileDir)
            if os.path.exists(file_path):
                doc = open(file_path, 'rb')
                response = HttpResponse(FileWrapper(doc), content_type=gcp.ext)
                response["Content-Length"] = gcp.size
                response['Content-Disposition'] = 'inline; filename=%s' % gcp.name
                return response
        return Response({"message":"not exist"})
# =========================GCP=========================================
