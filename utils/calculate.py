from math import sqrt

from django.contrib.gis.db.models.functions import Transform
from django.db.models import Sum
from imgs.models import Imgs

# 지정된 프로젝트의 업로드된 전체 이미지들을 사용해서 이미지 수량, 면적, 전체 용량 계산
def calculateImgArea(projectId, email):
    imgData = Imgs.objects.filter(projectId=projectId, email=email).annotate(loc=Transform('location', 3857))
    volume = imgData.aggregate(sum_of_volume=Sum("size"))
    loc = imgData.values_list('loc', flat=True)
    
    if len(loc) == 0:
        return 0, 0, 0
    x = []
    y = []
    for i in range(len(loc)):
        x.append(loc[i].x)
        y.append(loc[i].y)
    minX = min(x)
    minY = min(y)
    maxX = max(x)
    maxY = max(y)
    return len(loc), sqrt(pow((maxX - minX), 2) + pow((maxY - minY), 2)), volume["sum_of_volume"] # 이미지 개수, 면적, 전체 이미지 용량 리턴
