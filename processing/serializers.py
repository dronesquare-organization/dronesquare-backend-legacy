from rest_framework import serializers
from .models import Mosaics, Objects3D, Mtls, Textures, FastMosaics


# =========================MOSAICS====================================
class MosaicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mosaics
        fields = '__all__'
# =========================MOSAICS====================================

# =========================Texture====================================
class TextureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Textures
        fields = ('id', 'fileDir')
# =========================Texture====================================

# =========================MTL========================================
class MTLSerializer(serializers.ModelSerializer):
    mtl = serializers.CharField(read_only=True)
    class Meta:
        model = Mtls
        fields = (
            'id',
            'fileDir',
        )
# =========================MTL========================================

# =========================3D OBJECTS=================================
class Objects3DSerializer(serializers.ModelSerializer):
    class Meata:
        model = Objects3D
        fields = '__all__'

class Objects3DJoinSerializer(serializers.ModelSerializer):
    mtl = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='fileDir'
     )
    texture = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='fileDir'
     )
    class Meta:
        model = Objects3D
        fields = (
            'id',
            'projectId',
            'pcdFile',
            'pcdConvertedFile',
            'contourFile',
            'meshFile',
            'calibrated_external_camera_parameters',
            'coordSystem',
            'offsetXYZ',
            'mtl',
            'texture'
        )
# =========================3D OBJECTS=================================

# =========================FAST MOSAIC================================
class FastMosaicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FastMosaics
        fields = '__all__'
# =========================FAST MOSAIC================================