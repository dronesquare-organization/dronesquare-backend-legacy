# Python Libraries
import os
import math
from multiprocessing import Pool, Manager

# Django Apis
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum
from django.http import UnreadablePostError
from django.shortcuts import get_object_or_404

# Project Apps
from .models import Imgs
from .serializers import (
    ImgsSerializer,
    ImgsBrightSerializer,
    ImgsUpdateDibsSerializer,
)
from users.models import Users
from projects.models import Projects
from projects.serializers import ProjectUploadingSerializer

# Third Party Packages
import boto3
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from PIL import Image
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from tensorflow.python.keras.models import load_model

# utils
from utils.AutoFilterPredict import IE
from utils.calculate import calculateImgArea
from utils.ImgUploadSave import (
    imgSave,
    upload_to_aws,
    crfolder_tmp,
    path_settings,
    delfolder_exist,
    get_s3_path,
)
from utils.OptimizedDuplicate import optimizeDuplicate
from utils.RedundancyCalculate import IOR_F
from utils.Illumination import change_filter
# Create your views here.
# =========================IMGS=======================================
class NewImgsViewSet(viewsets.ViewSet):
    """새 이미지 뷰셋"""
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="이미지 업로드2(chunk upload upgrade)",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Authorization",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "projectId",
                in_=openapi.IN_FORM,
                description="projectId",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "file",
                in_=openapi.IN_FORM,
                description="file list",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_FILE),
            ),
        ],
    )
    def create(self, request):
        email = str(request.user)
        projectId = request.data["projectId"]
        accept = ["jpg", "jpeg", "png"]
        fail = []
        try:
            if type(request.data) != dict:
                file = request.FILES.getlist("file")[0]
                if file is None:
                    return Response({"message": "file is not exist"}, status=status.HTTP_404_NOT_FOUND)

                cr_path = path_settings(email, projectId)

                tmp_paths_name = [
                    "tmpPath",
                    "tmpCompression",
                    "tmpThumbnail",
                    "compression",
                    "tmpCheck",
                    "tmpPart",
                ]
                (
                    tmpPath,
                    tmpCompressionPath,
                    tmpThumbnailPath,
                    compressionPath,
                    tmpCheckPath,
                    tmpPartPath,
                ) = list(map(cr_path, tmp_paths_name))
                projectData = {
                    "id": request.data["projectId"],
                    "email": email,
                    "uploading": "진행중",
                }
                query_set = Projects.objects.all()
                project = get_object_or_404(
                    query_set, id=projectData["id"], email=email
                )
                serializer = ProjectUploadingSerializer(project, data=projectData)
                serializer.is_valid()
                serializer.save()
                if request.data["is_Start"] == "true":
                    # uploading 진행중

                    # 임시 폴더 있을 시 삭제 함수
                    delfolder_exist(
                        tmpPath,
                        tmpCompressionPath,
                        tmpThumbnailPath,
                        tmpCheckPath,
                        tmpPartPath,
                    )
                # 임시 폴더 생성 함수
                crfolder_tmp(email, projectId)

                destination = open(tmpPartPath + "/" + file.name, "wb")

                for chunk in file.chunks():
                    destination.write(chunk)
                destination.close()

                # check chunk file
                checkDestination = open(
                    tmpCheckPath
                    + "/"
                    + "".join(file.name.split(".part")[0].split(" "))
                    + ".txt",
                    "a+",
                )
                checkDestination.write(file.name + " ")
                checkDestination.close()
                checkDestination = open(
                    tmpCheckPath
                    + "/"
                    + "".join(file.name.split(".part")[0].split(" "))
                    + ".txt",
                    "r",
                )
                allFileName = list(checkDestination)
                allFileNameLength = len(allFileName[0].split(" ")) - 1
                checkDestination.close()
                isEnd = False

                if allFileNameLength == int(request.data["divided"]):
                    tmpFile = open(
                        tmpPath + "/" + "".join(file.name.split(".part")[0].split(" ")),
                        "ab+",
                    )
                    for part in range(allFileNameLength):
                        partFile = open(
                            tmpPartPath
                            + "/"
                            + file.name.split(".part")[0]
                            + ".part"
                            + str(part),
                            "rb",
                        )
                        tmpFile.write(partFile.read())
                        partFile.close()
                    tmpFile.close()
                    isEnd = True

                # check chunk file
                if isEnd and request.data["allFileLength"] == request.data["index"]:
                    user = Users.objects.get(email=email)
                    project = Projects.objects.get(id=request.data["projectId"])
                    Model_path = os.path.join(
                        os.getcwd(), "utils/files/model/TrainedNN_IE.h5"
                    )
                    NNmodel = load_model(Model_path)
                    onlyfiles = [
                        f
                        for f in os.listdir(tmpPath)
                        if os.path.isfile(os.path.join(tmpPath, f))
                    ]
                    # num_cores = multiprocessing.cpu_count()
                    num_cores = 4
                    # splited_data = [ x.tolist() for x in np.array_split(onlyfiles, num_cores)]

                    p = Pool(num_cores)
                    m = Manager()
                    fail_list = m.list()
                    divider = 0
                    if len(onlyfiles) <= num_cores:
                        divider = 1
                    else:
                        divider = math.ceil(float(len(onlyfiles) / num_cores))
                    print(divider)
                    # IE-RUN
                    isRtk = False
                    autoDeltaList = []
                    for f in onlyfiles:
                        auto = Image.open(tmpPath + "/" + f)
                        autoDelta = IE(auto, NNmodel)

                        if project.isRtk == False:
                            if len(auto.applist) > 1:
                                app, content = auto.applist[1]
                                index = str(content).find("RtkFlag", 0)
                                if index != -1:
                                    finder = str(content)[index : index + 16]
                                    RtkPoint = finder.split("RtkFlag=")[1].split('"')[1]
                                    if RtkPoint != 0:
                                        isRtk = True
                        auto.close()
                        autoDeltaList.append(autoDelta)

                    params = []
                    for i in range(num_cores):
                        if i == 0:
                            params.append(
                                [
                                    accept,
                                    fail_list,
                                    onlyfiles[:divider],
                                    autoDeltaList[:divider],
                                    tmpPath,
                                    compressionPath,
                                    tmpCompressionPath,
                                    tmpThumbnailPath,
                                    user,
                                    project,
                                ]
                            )
                        else:
                            params.append(
                                [
                                    accept,
                                    fail_list,
                                    onlyfiles[divider * i : divider * (i + 1)],
                                    autoDeltaList[divider * i : divider * (i + 1)],
                                    tmpPath,
                                    compressionPath,
                                    tmpCompressionPath,
                                    tmpThumbnailPath,
                                    user,
                                    project,
                                ]
                            )
                    p.map(imgSave, params)
                    p.close()
                    duplicate = None

                    if len(onlyfiles) >= 10:
                        duplicate = IOR_F(tmpPath)
                    for i in range(len(onlyfiles)):
                        upload_to_aws(tmpPath + "/" + onlyfiles[i])
                    delfolder_exist(
                        tmpPath,
                        tmpCompressionPath,
                        tmpThumbnailPath,
                        tmpCheckPath,
                        tmpPartPath,
                    )

                    imgList = Imgs.objects.filter(
                        projectId=request.data["projectId"], email=email
                    ).order_by("created")
                    imgSerializer = ImgsSerializer(imgList, many=True)
                    result = Imgs.objects.filter(
                        email=email, projectId=request.data["projectId"]
                    ).aggregate(sum_of_size=Sum("size"))
                    projectData = {
                        "id": request.data["projectId"],
                        "email": email,
                        "uploading": "완료",
                    }
                    if result["sum_of_size"] is not None:
                        projectData["imgVolume"] = result["sum_of_size"]
                    else:
                        projectData["imgVolume"] = 0
                    if (
                        duplicate is not None
                        and project.duplicate_rate + project.duplicate_std
                        < duplicate[0] + duplicate[1]
                    ):
                        projectData["duplicate_rate"] = duplicate[0]
                        projectData["duplicate_std"] = duplicate[1]
                    else:
                        projectData["duplicate_rate"] = project.duplicate_rate
                        projectData["duplicate_std"] = project.duplicate_std
                    imgCnt, area, volume = calculateImgArea(
                        request.data["projectId"], email
                    )

                    projectData["imgCnt"] = imgCnt
                    projectData["area"] = area
                    projectData["isRtk"] = isRtk
                    if len(imgSerializer.data) != 0:
                        projectData["img_created"] = dict(
                            imgSerializer.data[0].items()
                        )["created"]
                    else:
                        projectData["img_created"] = None
                    serializer = ProjectUploadingSerializer(project, data=projectData)

                    serializer.is_valid()
                    serializer.save()

                    return Response({"fail": fail, "imgs": imgSerializer.data})
            projectData = {
                "id": request.data["projectId"],
                "email": email,
                "uploading": "완료",
            }
            query_set = Projects.objects.all()
            project = get_object_or_404(query_set, id=projectData["id"], email=email)
            serializer = ProjectUploadingSerializer(project, data=projectData)
            serializer.is_valid()
            serializer.save()
            return Response({"message": "continue"})
        except UnreadablePostError:
            projectData = {
                "id": request.data["projectId"],
                "email": email,
                "uploading": "완료",
            }
            query_set = Projects.objects.all()
            project = get_object_or_404(query_set, id=projectData["id"], email=email)
            serializer = ProjectUploadingSerializer(project, data=projectData)
            serializer.is_valid()
            serializer.save()
            return Response({"message": "disconnect"})


class ImgsListViewSet(viewsets.ViewSet):
    """이미지 리스트 뷰셋"""

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="이미지 리스트 조회",
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
    def lists(self, request, projectId):
        email = str(request.user)

        imgList = Imgs.objects.filter(projectId=projectId, email=email).order_by(
            "created"
        )
        serializer = ImgsSerializer(imgList, many=True)

        return Response(serializer.data)


class ImgsViewSet(viewsets.ViewSet):
    """이미지 뷰셋"""

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="이미지 삭제",
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
            ),
            openapi.Parameter(
                "projectId",
                openapi.IN_PATH,
                description="PROJECT ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    @action(detail=False, methods=["patch"], url_path=r"(?P<projectId>\d+)")
    def imgs(self, request, projectId):
        email = str(request.user)
        idSet = request.data["idSet"]
        imgs = Imgs.objects.filter(projectId=projectId, email=email, id__in=idSet)

        if imgs.exists():
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            for img in imgs:
                path_list = ["compression", "thumbnail", "original"]
                s3_path = get_s3_path(email, projectId, img.name)
                s3_path_list = list(map(s3_path, path_list))

                for key in s3_path_list:
                    if key.split("/")[0] == "media":
                        response = s3_client.delete_object(
                            Bucket="droneplatform", Key=key
                        )
                    else:
                        response = s3_client.delete_object(
                            Bucket="original-drone-image", Key=key
                        )

            imgs.delete()
            imgCnt, area, volume = calculateImgArea(projectId, email)
            project = Projects.objects.filter(email=email, id=projectId)
            if project.exists():
                project.update(imgCnt=imgCnt, area=area, imgVolume=volume)
                if imgCnt == 0:
                    project.update(img_created=None)
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        return Response({"message": "empty"})


class ImgsBrightViewSet(viewsets.ViewSet):
    """이미지 밝기 뷰셋"""

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="이미지 밝기값 조절",
        request_body=ImgsBrightSerializer,
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
        request.data["email"] = email
        img = Imgs.objects.get(id=pk, projectId=request.data["projectId"], email=email)
        originFile = "media/" + str(img.fileDir)

        destinationDir = None
        filtered_img = None
        original = False
        try:
            if float(request.data["illuminationDelta"]) == 0:
                img.illuminationDelta = 0
                destinationDir = str(img.fileDir)
                original = True
            else:
                filtered_img = change_filter(
                    originFile, float(request.data["illuminationDelta"]), img
                )
                destinationDir = "{email}/projects/{projectId}/bright/{file}".format(
                    email=str(email),
                    projectId=request.data["projectId"],
                    file="filtered_" + img.name,
                )
                img.filterDir = destinationDir
                img.illuminationDelta = float(request.data["illuminationDelta"])
                original = False
            img.save()
            print("is filtering?", not original, flush=True)
            return Response({"filterDir": destinationDir, "origin": original})
        except FileNotFoundError:
            print(FileNotFoundError)
            return Response({"message": "not exsit"}, status=status.HTTP_404_NOT_FOUND)


class ImgsUpdateDibsViewSet(viewsets.ViewSet):
    """이미지 찜하기 업데이트 뷰셋"""

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="이미지 찜하기 업데이트",
        request_body=ImgsUpdateDibsSerializer,
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
        detail=False, methods=["patch"], url_path=r"(?P<projectId>\d+)/(?P<imgId>\d+)"
    )
    def dibs(self, request, projectId, imgId):
        email = request.user
        try:
            imgsData = Imgs.objects.get(id=imgId, projectId=projectId, email=email)
            imgsData.isDibs = request.data["isDibs"]
            imgsData.save()
            return Response({"message": "succes"})
        except ObjectDoesNotExist:
            return Response({"message": "empty"}, status=status.HTTP_404_NOT_FOUND)


# =========================IMGS=======================================
