from rest_framework import serializers
from .models import Layers2D, Layers2D3D

# =========================LAYERS2D===================================
class Layers2DSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layers2D
        fields = (
            "id",
            "properties",
            "created",
            "modified",
            "imgId",
            "projectId",
            "email",
            "issueCnt",
        )

class Layers2DInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layers2D
        fields = ("id", "properties", "created", "modified", "imgId", "projectId")
# =========================LAYERS2D===================================

# =========================LAYERS2D&3D================================
class Layers2D3DInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layers2D3D
        fields = ('id', 'properties', 'created', 'modified', 'mosaicId', 'projectId')


class Layers2D3DSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layers2D3D
        fields = '__all__'

class Layers2D3DPropInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layers2D3D
        fields = ('id','properties')

class Layers2D3DListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layers2D3D
        fields = ('id', 'properties', 'created', 'modified')

# =========================LAYERS2D&3D================================