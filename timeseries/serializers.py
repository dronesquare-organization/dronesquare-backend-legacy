from rest_framework import serializers
from projects.serializers import ProjectsSerializer
from .models import TimeSeries, TimeSeriesRelation

# =========================TIMESERIES=================================
class TimeSeriesRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSeriesRelation
        fields = "__all__"


class TimeSeriesRelationInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSeriesRelation
        fields = (
            "timeseriesId",
            "projectInfo",
        )


class TimeSeriesJoinSerializer(serializers.ModelSerializer):
    projectInfo = ProjectsSerializer(read_only=True)

    class Meta:
        model = TimeSeriesRelation
        fields = ("id", "projectInfo")


class TimeSeriesSerializer(serializers.ModelSerializer):
    relation = TimeSeriesJoinSerializer(many=True, read_only=True)

    class Meta:
        model = TimeSeries
        fields = ("id", "name", "email", "created", "modified", "relation")


class TimeSeriesRelationByProjectIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSeries
        fields = ("id", "name")


class TimeSeriesInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSeries
        fields = ("name",)

# =========================TIMESERIES=================================
