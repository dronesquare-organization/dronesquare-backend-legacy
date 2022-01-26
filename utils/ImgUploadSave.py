from math import log
from PIL import Image
from PIL.ExifTags import TAGS
from utils.DuplicateName import createFileName
from utils.Compression import compressionImage
from utils.GetMetaData import getMetaData
from utils.AutoFilterPredict import IE
from django.core.files.base import File
from imgs.models import Imgs
import shutil
import os
import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError


def imgSave(param):
    (
        accept,
        fail,
        onlyfiles,
        autoDelta,
        tmpPath,
        compressionPath,
        tmpCompressionPath,
        tmpThumbnailPath,
        user,
        project,
    ) = param
    for i in range(len(onlyfiles)):  # tmp path file name
        if onlyfiles[i].split(".")[-1].lower() in accept:
            # metadata checking start
            im = Image.open(tmpPath + "/" + onlyfiles[i])
            metadata = {
                "width": im.size[0],
                "height": im.size[1],
                "size": os.path.getsize(tmpPath + "/" + onlyfiles[i]),
            }
            tagLabel = {}
            info = im.getexif()

            if info != {} and info is not None:
                fileName = createFileName(
                    compressionPath + "/" + "".join(onlyfiles[i].split(" ")),
                    onlyfiles[i],
                )
                # compression maker
                compressionImage(im, tmpCompressionPath + "/" + onlyfiles[i])

                for tag, value in info.items():
                    decoded = TAGS.get(tag, tag)

                    tagLabel[decoded] = value
                metadata.update(getMetaData(tagLabel))

                # autoDeltaValue = autoDelta[i]
                # # thumbnail
                thumbnail = im.resize((256, 256))
                thumbnail.save(tmpThumbnailPath + "/" + fileName, quality=95)
                metadata["name"] = fileName
                metadata["format"] = "image/" + fileName.split(".")[1]
                metadata["email"] = user
                metadata["projectId"] = project
                # metadata["autoDelta"] = autoDeltaValue
                com = open(tmpCompressionPath + "/" + onlyfiles[i], "rb")
                thum = open(tmpThumbnailPath + "/" + fileName, "rb")
                metadata["fileDir"] = File(com, name=onlyfiles[i])
                metadata["thumbnail"] = File(thum, name=fileName)

                Img = Imgs(**metadata)
                Img.save()
                im.close()
                com.close()
                thum.close()
            else:
                fail.append(onlyfiles[i])
        else:
            fail.append(onlyfiles[i])


def path_settings(email, projectId):
    """해당 폴더 경로 생성"""
    email = email
    projectId = projectId

    def path_setting_join(path):
        return settings.MEDIA_ROOT + "/" + email + "/projects/" + projectId + "/" + path

    return path_setting_join


def path_settings_gcp(email, projectId):
    """해당 폴더 경로 생성"""
    email = email
    projectId = projectId

    def path_setting_join(path):
        return "/tmp/" + email + "/projects/" + projectId + "/" + path

    return path_setting_join


def get_s3_path(email, projectId, name):
    email = email
    projectId = projectId
    name = name

    def path_setting_join(path):
        if path is "original":
            return "{email}/projects/{projectId}/{name}".format(
                email=email, projectId=projectId, name=name
            )
        else:
            return "media/{email}/projects/{projectId}/{path}/{name}".format(
                email=email, projectId=projectId, path=path, name=name
            )

    return path_setting_join


def delfolder_exist(*paths):
    """해당 폴더 있을 시 삭제"""
    for path in paths:
        if os.path.exists(path):
            shutil.rmtree(path)


def crfolder_tmp(email, projectId):
    """임시폴더 생성"""
    bsdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/media"
    folder_list = ["Path", "Check", "Thumbnail", "Part", "Compression"]

    for folder in folder_list:
        path = bsdir + "/" + email + "/projects/" + projectId + "/tmp" + folder
        if not os.path.exists(path):
            os.makedirs(path)


def create_tmpfolder(email, projectId, *folderList):
    """임시폴더 생성"""
    for folder in folderList:
        path = "/tmp/" + email + "/projects/" + projectId + "/" + folder
        if not os.path.exists(path):
            os.makedirs(path)


def upload_to_aws(local_name):
    """original file aws upload 함수"""
    s3_name = (
        local_name.replace("media", "original")
        .replace("/tmpPath", "")
        .split("original/")[1]
    )
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    try:
        response = s3_client.upload_file(local_name, "original-drone-image", s3_name)
        return True
    except FileNotFoundError:
        return False
    except NoCredentialsError:
        return False


class UploadFilesToS3:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def search_file(self, dirname):
        """etc file aws upload"""
        try:
            filenames = os.listdir(dirname)
            for filename in filenames:
                full_filename = os.path.join(dirname, filename)
                if os.path.isdir(full_filename):
                    self.search_file(full_filename)
                else:
                    s3_name = full_filename[full_filename.find("media") :]
                    self.s3_client.upload_file(full_filename, "droneplatform", s3_name)
        except PermissionError:
            pass
