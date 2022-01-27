from django.urls import path
from etcs.views import VideoViewSet
from rest_framework.routers import DefaultRouter

app_name = "etcs"

router = routers.DefaultRouter()

router.register("videos", VideoViewSet)
router.register("")

urlpatterns = [
    router.urls,
]
