import uuid
from django.conf import settings
import os

def originalImg_upload_path(instance, filename):
    return os.path.join(
        "{email}/projects/{projectId}/originalImgs".format(
            email=instance.email, projectId=instance.projectId
        ),
        instance.name,
    )
def compressionImg_upload_path(instance, filename):
    return os.path.join(
        "{email}/projects/{projectId}/compression".format(
            email=instance.email, projectId=instance.projectId
        ),
        instance.name,
    )
def thunmbnailImg_upload_path(instance, filename):
    return os.path.join(
        "{email}/projects/{projectId}/thumbnail".format(
            email=instance.email, projectId=instance.projectId
        ),
        instance.name,
    )
def video_upload_path(instance, filename):
    return os.path.join(
        "{email}/projects/{projectId}/etcVideo".format(
            email=instance.email, projectId=instance.projectId
        ),
        instance.name,
    )

def etc_upload_path(instance, filename):
    return os.path.join(
        "{email}/projects/{projectId}/etc".format(
            email=instance.email, projectId=instance.projectId
        ),
        instance.name,
    )
def nestedLayer_upload_path(instance, filename):  
    return os.path.join(
        "{email}/projects/{projectId}/nestedLayer".format(
            email=instance.email, projectId=instance.projectId
        ),
        instance.name,
    )
def etcImg_upload_path(instance, filename):   
    return os.path.join(
        "{email}/projects/{projectId}/etcImg".format(
            email=instance.email, projectId=instance.projectId
        ),
        instance.name,
    )
def etcDoc_upload_path(instance, filename): 
    return os.path.join(
        "{email}/projects/{projectId}/etcDoc".format(
            email=instance.email, projectId=instance.projectId
        ),
        instance.name,
    )
def etc2D3D_upload_path(instance, filename):   
    return os.path.join(
        "{email}/projects/{projectId}/etc2D3D".format(
            email=instance.email, projectId=instance.projectId
        ),
        instance.name,
    )
def gcp_upload_path(instance, filename):
    return os.path.join(
        "{email}/projects/{projectId}/gcp".format(
            email=instance.email, projectId=instance.projectId
        ),
        instance.name,
    )