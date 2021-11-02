from drf_braces.serializers.form_serializer import FormSerializer
from rest_framework import serializers
from .forms import ImgUploadForm
from .models import Imgs


# =========================IMGS=======================================
class ImgsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imgs
        fields = "__all__"


class ImgsUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imgs
        fields = ("projectId", "email", "fileDir")


class ImgsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imgs
        fields = ("projectId", "email")


class ImgsBrightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imgs
        fields = ("projectId", "id", "illuminationDelta")


class ImgsUpdateDibsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imgs
        fields = ("isDibs",)


# =========================IMGS=======================================