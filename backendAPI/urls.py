"""backendAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from etcs.views import (Etc2D3DLayersDeleteViewSet,
                        Etc2D3DLayersDownloadViewSet, Etc2D3DLayersListViewSet,
                        Etc2D3DLayersViewSet, EtcDocsDeleteViewSet,
                        EtcDocsDownloadViewSet, EtcDocsListViewSet,
                        EtcDocsViewSet, EtcImgsDeleteViewSet,
                        EtcImgsDownloadViewSet, EtcImgsListViewSet,
                        EtcImgsViewSet, GCPDeleteViewSet, GCPDownloadViewSet,
                        GCPListViewSet, GCPViewSet, NestedLayersDeleteViewSet,
                        NestedLayersDownloadViewSet, NestedLayersListViewSet, NestedLayersUpdateViewSet,
                        NestedLayersViewSet, VideoDeleteViewSet,
                        VideoDownloadViewSet, VideoListViewSet, VideoViewSet)
from imgs.views import (ImgsBrightViewSet, ImgsListViewSet,
                        ImgsUpdateDibsViewSet, ImgsViewSet, NewImgsViewSet)
from layers.views import (CalculateViewSet, CalculateVolumeViewSet,
                          Layers2D3DListViewSet, Layers2D3DPropViewSet,
                          Layers2D3DViewSet, Layers2DListViewSet,
                          Layers2DViewSet, LocationViewSet)
from processing.views import MosaicsViewSet, VoxelViewSet, Objects3DViewerViewSet, FastMosaicsViewSet
from projects.views import (AnomalyDegreeViewSet, AnomalyTypesViewSet,
                            DataProcessFileViewSet, DataProcessViewSet,
                            NewProjectsViewSet, ProjectsDetailViewSet,
                            ProjectsListViewSet)
from rest_framework import permissions, routers
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)
from timeseries.views import (TimeSeriesFindByProjectViewSet,
                              TimeSeriesRelationViewSet, TimeSeriesViewSet)
from users.views import (LogoutView, LoginView, PaymentViewSet, RegistrationViewSet,
                         StorageDetailViewSet, UserInfoViewSet, EmailActiveViewSet,
                         UserPasswordViewSet, CheckingEmailViewSet)

router = routers.DefaultRouter()
router.register("etc/video", VideoViewSet, basename="video")
router.register("etc/video", VideoDeleteViewSet, basename="videoDelete")
router.register("etc/video/list", VideoListViewSet, basename="videoList")
router.register("etc/video/download", VideoDownloadViewSet, basename="videoDownload")
router.register("etc/img", EtcImgsViewSet, basename="etcImgUpload")
router.register("etc/img", EtcImgsDeleteViewSet, basename="etcImgDelete")
router.register("etc/img/list", EtcImgsListViewSet, basename="etcImgList")
router.register("etc/img/download", EtcImgsDownloadViewSet, basename="etcImgDownload")
router.register("etc/doc", EtcDocsViewSet, basename="EtcDocUpload")
router.register("etc/doc", EtcDocsDeleteViewSet, basename="EtcDocDelete")
router.register("etc/doc/list", EtcDocsListViewSet, basename="EtcDocList")
router.register("etc/doc/download", EtcDocsDownloadViewSet, basename="EtcDocDownload")
router.register("etc/nested-layer", NestedLayersViewSet, basename="NestedLayersUpload")
router.register("etc/nested-layer/enrollment", NestedLayersUpdateViewSet, basename="NestedLayersUpdateViewSet")
router.register("etc/nested-layer", NestedLayersDeleteViewSet, basename="NestedLayersDelete")
router.register("etc/nested-layer/list", NestedLayersListViewSet, basename="NestedLayersList")
router.register("etc/nested-layer/download", NestedLayersDownloadViewSet, basename="NestedLayersDownload")
router.register("etc/2d-3d-layer", Etc2D3DLayersViewSet, basename="Etc2D3DLayersUpload")
router.register("etc/2d-3d-layer", Etc2D3DLayersDeleteViewSet, basename="Etc2D3DLayersDelete")
router.register("etc/2d-3d-layer/list", Etc2D3DLayersListViewSet, basename="Etc2D3DLayersList")
router.register("etc/2d-3d-layer/download", Etc2D3DLayersDownloadViewSet, basename="Etc2D3DLayersDownload")
router.register("gcp", GCPViewSet, basename="Etc2D3DLayersUpload")
router.register("gcp", GCPDeleteViewSet, basename="Etc2D3DLayersDelete")
router.register("gcp/list", GCPListViewSet, basename="Etc2D3DLayersList")
router.register("gcp/download", GCPDownloadViewSet, basename="Etc2D3DLayersDownload")

router.register("imgs/filter", ImgsBrightViewSet, basename="ImgsBright")
router.register("imgs/dibs", ImgsUpdateDibsViewSet, basename="imgsDibsUpdate")
router.register("imgs/upload", NewImgsViewSet, basename="imgsUpload")
router.register("imgs/list", ImgsListViewSet, basename="imgsList")
router.register("imgs", ImgsViewSet, basename="img")

router.register("2d-layers", Layers2DViewSet, basename="2DLayers")
router.register("2d-layers/list", Layers2DListViewSet, basename="2DLayersList")
router.register("2d-3d-layers", Layers2D3DViewSet, basename="2D3DLayers")
router.register("2d-3d-layers/list", Layers2D3DListViewSet, basename="2D3DLayersList")
router.register("2d-3d-layers/propInfo", Layers2D3DPropViewSet, basename="2D3DLayersList")
router.register("location", LocationViewSet, basename="get_Location")
router.register("calculation", CalculateViewSet, basename="calculate_easy")

router.register("mosaic", MosaicsViewSet, basename="mosaicData")
router.register("voxel", VoxelViewSet, basename="VoxelFind")
router.register("object", Objects3DViewerViewSet, basename="Objects3DViewer_Info")
router.register("fast-mosaic", FastMosaicsViewSet, basename="FastMosaic")

router.register("data-process", DataProcessViewSet, basename="data_process_request")
router.register("data-process-file", DataProcessFileViewSet, basename="data_process_file")
router.register("project/new", NewProjectsViewSet, basename="project")
router.register("project/list", ProjectsListViewSet, basename="projectList")
router.register("project", ProjectsDetailViewSet, basename="projectDetail")
router.register("anomaly-type", AnomalyTypesViewSet, basename="AnomalyTypesViewSet")
router.register("anomaly-degree", AnomalyDegreeViewSet, basename="AnomalyDegreeViewSet")

router.register("timeseries", TimeSeriesViewSet, basename="TimeSeries")
router.register("timeseries-relation", TimeSeriesRelationViewSet, basename="TimeSeriesRelation")
router.register('timeseries-project', TimeSeriesFindByProjectViewSet, basename="findTimeseriesByProject")

router.register("user/registration", RegistrationViewSet, basename="registration")
router.register("user/verification", CheckingEmailViewSet, basename="checkinEmailViewSet")
router.register("user/password", UserPasswordViewSet, basename="userPassword")
router.register("user/info", UserInfoViewSet, basename="info")
router.register("user/storage", StorageDetailViewSet, basename="storage")
router.register("user/payment", PaymentViewSet, basename="payment")
router.register("user/email-verification", EmailActiveViewSet, basename="email_validation")

schema_view = get_schema_view(
    openapi.Info(
        title="Backend API",
        default_version="v1.0.1",
        description="django API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(name="test", email="test@test.com"),
        license=openapi.License(name="Test License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path("api/v1/user/login/", LoginView.as_view()),
    path("api/v1/refresh/", TokenRefreshView.as_view()),
    path("api/v1/user/logout/", LogoutView.as_view()),
    path("api/v1/verify/", TokenVerifyView.as_view()),
    path("", include("default.urls"))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        re_path(
            r"^swagger/$",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        re_path(
            r"^redoc/$",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
    ]
