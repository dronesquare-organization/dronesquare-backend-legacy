from drf_braces.serializers.form_serializer import FormSerializer
from rest_framework import serializers
from .models import Video, EtcImgs, EtcDocs, Etc2D3DLayers, NestedLayers, GCP

# =========================VIDEO===================================
class VideoListUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False)
    )

    def create(self, validated_data):
        files = validated_data.pop("files")
        for file in files:
            f = Video.objects.create(fileDir=file)
        return f


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"


# =========================VIDEO===================================

# =========================NESTEDLAYER=============================
class NestedLayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = NestedLayers
        fields = "__all__"


# =========================NESTEDLAYER=============================

# =========================ETCIMGS===================================
class EtcImgsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtcImgs
        fields = "__all__"


# =========================ETCIMGS===================================

# =========================ETCDOCS===================================
class EtcDocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EtcDocs
        fields = "__all__"


# =========================ETCDOCS===================================

# =========================ETCDOCS===================================
class Etc2D3DLayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etc2D3DLayers
        fields = "__all__"


# =========================ETCDOCS===================================

# =========================GCP=======================================
class GCPSerializer(serializers.ModelSerializer):
    class Meta:
        model = GCP
        fields = "__all__"


# =========================GCP=======================================
