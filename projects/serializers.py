from drf_braces.serializers.form_serializer import FormSerializer
from rest_framework import serializers
from .models import Projects, DataProcess, DataProcessFile

# =========================DATA-PROCESS===============================
class DataProcessInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataProcess
        fields = (
            "projectId", 
            "quality_low", 
            "quality_mid", 
            "quality_high", 
            "quality", 
            "processOption", 
            "request_memo"
        )

class DataProcessSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataProcess
        fields = (
            "projectId", 
            "quality_low", 
            "quality_mid", 
            "quality_high", 
            "quality", 
            "processOption", 
            "request_memo",
            "email"
        )

class DataProcessReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataProcess
        fields = ("id", "projectId", "quality_low", "quality_mid", "quality_high", "quality", "processOption", "request_memo", "notice", "gsd", "admin_upload", "mosaicResolution", "pointDensity", "precision_x", "precision_y", "precision_z", "precision_rmse", "processStatus", "applyProcess", "completedProcess", "coordinateSystem")
# =========================DATA-PROCESS===============================

# =========================PROJECTS===================================
class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = "__all__"

class ProjectFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = (
            "areaName",
            "assetName",
            "projectName",
            "location",
            "assetType",
            "comment",
        )

class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = (
            "areaName",
            "assetName",
            "projectName",
            "comment",
            "shared",
            "assetType",
        )

class ProjectUploadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ("id", "email", "uploading", "imgVolume", "img_created", "imgCnt", "area", "duplicate_rate", "duplicate_std", "isRtk")

class ProjectJoinDataProcessSerializer(serializers.ModelSerializer):
    dataprocess = DataProcessReadSerializer(read_only=True)
    class Meta:
        model = Projects
        fields = (
            "id",
            "areaName",
            "assetName",
            "assetType",
            "projectName",
            "created",
            "modified",
            "shared",
            "imgCnt",
            "comment",
            "location",
            "uploading",
            "img_created",
            "area",
            "issueCnt",
            "timeSeriesCnt",
            "isRtk",
            "duplicate_rate",
            "duplicate_std",
            "dataprocess"
        )
# =========================PROJECTS===================================

# =========================DATA-PROCESS-FILE==========================
class DataProcessFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataProcessFile
        fields = "__all__"
# =========================DATA-PROCESS-FILE==========================

