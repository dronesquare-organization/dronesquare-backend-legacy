from django.db.models.signals import post_delete
from django.dispatch import receiver
from .serializers import TimeSeriesRelationSerializer
from projects.models import Projects
from .models import TimeSeriesRelation


# when TimeSeries Relation Delete
@receiver(post_delete, sender=TimeSeriesRelation)
def TimeSeriesRelation_post_delete(sender, **kwargs):
    serializer = TimeSeriesRelationSerializer(kwargs["instance"])
    cntOfRelation = len(TimeSeriesRelation.objects.filter(projectInfo=serializer.data["projectInfo"], email=serializer.data["email"]))
    project = Projects.objects.filter(id=serializer.data["projectInfo"], email=serializer.data["email"])
    project.update(timeSeriesCnt=cntOfRelation)