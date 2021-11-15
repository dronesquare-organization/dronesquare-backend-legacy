import os
import datetime
import numpy as np
import math
import rasterio
from pyproj import Transformer, transformer
from rasterio.mask import mask
from backendAPI import settings


def transform_coordinate(origin, destination, data, type_of_method): # 좌표계 변환 후 GeoJSON 폴리곤 포맷으로 변환
    transformResult = []
    points = []

    transformer = Transformer.from_crs(int(origin), int(destination), always_xy=True)
    if type_of_method == "Polygon":
        for coord in data:
            points.append((coord[0], coord[1]))

        for pt in transformer.itransform(points):
            transformResult.append([pt[0], pt[1]])
    else:
        points = [
            (data[0], data[1])
        ]
        for pt in transformer.itransform(points):
            transformResult = [pt[0], pt[1]]

    return transformResult


def PointToPoint3Distance(a1, a2):
    if a1[2] == -10000 or a2[2] == -10000:
        return "-"
    return math.sqrt(pow((a1[0] - a2[0]), 2) + pow((a1[1] - a2[1]), 2) + pow((a1[2] - a2[2]), 2))


def PointToPoint2Distance(a1, a2):
    return math.sqrt(pow((a1[0] - a2[0]), 2) + pow((a1[1] - a2[1]), 2))


def calculate3DArea(arr, points):
    distance = []
    totalArea = [0, 0, 0]
    elevation = []
    angle = []
    position = []
    invalid = False
    for i in range(1, len(arr)):
        if -10000 in arr[i-1] or -10000 in arr[i]:
            invalid = True
        prod = np.cross(arr[i - 1], arr[i])
        totalArea[0] += prod[0]
        totalArea[1] += prod[1]
        totalArea[2] += prod[2]
        position.append([points[i - 1][0], points[i - 1][1], arr[i - 1][2]])
        if arr[i][2] == -10000 or arr[i - 1][2] == -10000:
            elevation.append("-")
        else:
            elevation.append(arr[i][2] - arr[i - 1][2])
        distance.append(PointToPoint3Distance(arr[i - 1], arr[i]))
        if PointToPoint3Distance(arr[i - 1], arr[i]) == "-":
            angle.append("-")
        else:
            angle.append(-180/math.pi if arr[i-1]<arr[i] else 180/math.pi *
                math.acos(float(PointToPoint2Distance(arr[i - 1], arr[i]) / PointToPoint3Distance(arr[i - 1], arr[i]))))
    measureResult = math.sqrt(totalArea[0] * totalArea[0] + totalArea[1] * totalArea[1] + totalArea[2] * totalArea[2])
    position.append([points[len(arr) - 1][0], points[len(arr) - 1][1], arr[len(arr) - 1][2]])
    return {"d3": measureResult if invalid==False else "-", "position": position,
            "segment": {"d3": distance, "elevation": elevation, "angle": angle}}


def calculate3DDistance(arr, points): # 측정에서 점 사이 거리 측정할 때 사용
    distance = []
    angle = []
    elevation = []
    position = []
    invalid = False
    for i in range(1, len(arr)):
        position.append([points[i - 1][0], points[i - 1][1], arr[i - 1][2]])
        if arr[i][2] == -10000 or arr[i - 1][2] == -10000:
            elevation.append("-")
        else:
            elevation.append(arr[i][2] - arr[i - 1][2])
        distance.append(PointToPoint3Distance(arr[i - 1], arr[i]))
        if PointToPoint3Distance(arr[i - 1], arr[i]) == "-":
            angle.append("-")
            invalid = True
        else:
            angle.append(-180/math.pi if arr[i-1]<arr[i] else 180/math.pi *
                math.acos(float(PointToPoint2Distance(arr[i - 1], arr[i]) / PointToPoint3Distance(arr[i - 1], arr[i]))))
    position.append([points[len(arr) - 1][0], points[len(arr) - 1][1], arr[len(arr) - 1][2]])
    return {"d3": sum(distance) if invalid==False else "-" , "position": position,
            "segment": {"d3": distance, "elevation": elevation, "angle": angle}}


def calculateByDSM(inputGeoJson, referencesData): # 상위 2개 함수 사용하여 넓이나 거리 구하는 메서드
    typeOfJson = inputGeoJson[0]['type']

    if typeOfJson != 'Point':
        points = []
        if typeOfJson == "Polygon":
            transformResult = transform_coordinate(3857, int(referencesData.coordSystem),
                                                   inputGeoJson[0]["coordinates"][0], "Polygon")
            for coord in inputGeoJson[0]['coordinates'][0]:
                points.append((coord[0], coord[1]))
        else:
            line_transformResult = transform_coordinate(3857, int(referencesData.coordSystem),
                                                        inputGeoJson[0]["coordinates"], "Polygon")
            if len(line_transformResult) < 4:
                line_x = []
                line_y = []
                for coord in line_transformResult:
                    line_x.append(coord[0])
                    line_y.append(coord[1])
                transformResult = [[min(line_x), min(line_y)], [max(line_x), min(line_y)], [max(line_x), max(line_y)], [min(line_x), max(line_y)]]
            else:
                transformResult = line_transformResult
            for coord in inputGeoJson[0]['coordinates']:
                points.append((coord[0], coord[1]))
        if typeOfJson == "LineString":
            inputGeoJson[0]["type"] = "Polygon"

        inputGeoJson[0]['coordinates'] = [transformResult]
    else:
        x = inputGeoJson[0]["coordinates"][0]
        y = inputGeoJson[0]["coordinates"][1]
        xmin = x-0.001
        xmax = x+0.001
        ymin = y-0.001
        ymax = y+0.001
        inputGeoJson[0]['type'] = "Polygon"
        inputGeoJson[0]['coordinates'] = [[[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]]
        transformResult = transform_coordinate(3857, int(referencesData.coordSystem),
                                               inputGeoJson[0]["coordinates"][0], "Polygon")
        targetResult = transform_coordinate(3857, int(referencesData.coordSystem), [x, y],
                                           "Point")
        inputGeoJson[0]['coordinates'] = [transformResult]

    try:
        if settings.DEV_LOCAL:
            dsm = os.path.split(settings.MEDIA_ROOT)[0] + referencesData.dsmDir
        else:
            dsm = 's3://droneplatform{}'.format(referencesData.dsmDir)

        with rasterio.Env(aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name="ap-northeast-2", AWS_S3_ENDPOINT='s3.ap-northeast-2.amazonaws.com'):
            with rasterio.open(dsm) as file:
                out_image, out_transform = mask(file, inputGeoJson, crop=True, all_touched=True, nodata=-10000)

        out_meta = file.meta
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})

        tmpSaveDir = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/processing/tmp".format(
            email=referencesData.email,
            projectId=referencesData.projectId)
        if not os.path.exists(tmpSaveDir):
            os.makedirs(tmpSaveDir)
        dateToFileName = "".join(str(datetime.datetime.now()).replace(":", "").replace(".", "").split(" ")) + "00"

        with rasterio.open(tmpSaveDir + "/" + dateToFileName + ".tif", "w", **out_meta) as dest:
            dest.write(out_image)
        with rasterio.open(tmpSaveDir + "/" + dateToFileName + ".tif", "r") as tmpRead:
            tmpReader = tmpRead.read(1)
        calculateResult = None
        if typeOfJson != "Point":
            arr = []
            if typeOfJson == "Polygon":
                for i in transformResult:
                    row, col = tmpRead.index(i[0], i[1])
                    if col > len(tmpReader[row]):
                        arr.append([i[0], i[1], -10000])
                    else:
                        arr.append([i[0], i[1], tmpReader[row, col]])
                # print("result!!! : ", calculate3DArea(arr))
                calculateResult = calculate3DArea(arr, points)
            else:
                for i in line_transformResult:
                    row, col = tmpRead.index(i[0], i[1])
                    if col > len(tmpReader[row]):
                        arr.append([i[0], i[1], -10000])
                    else:
                        arr.append([i[0], i[1], tmpReader[row, col]])
                # print("result!!! : ", calculate3DDistance(arr))
                calculateResult = calculate3DDistance(arr, points)
        else:
            row, col = tmpRead.index(targetResult[0], targetResult[1])
            if col > len(tmpReader[row]):
                calculateResult = {"position": [x, y, -10000]}
            else:
                calculateResult = {"position": [x, y, tmpReader[row, col]]}

        os.remove(tmpSaveDir + "/" + dateToFileName + ".tif")
        return calculateResult
    except FileNotFoundError as e:
        print(e)


def volume_by_bottom_total(out_image, minz, gsd):  # 전체 볼륨 계산(체적 정보) minz - 바닥면 높이 설정값, gsd - Dsm 가준 1픽셀당 실제 거리값
    changed = np.array(out_image, dtype=np.float64)
    result = np.sum(changed[changed != -10000] - minz, dtype=np.float64) * (gsd * gsd)
    return result


def volume_by_bottom_fill(out_image, minz, gsd):  # 볼륨 채우기 
    changed = np.array(out_image, dtype=np.float64)
    changed[changed != -10000] -= minz
    result = np.sum(np.sum(changed, axis=1, where=((changed != -10000) & (changed < 0)), dtype=np.float64),
                    dtype=np.float64) * (gsd * gsd)
    return result


def surface_by_bottom(out_image, minz, gsd): # 3D 표면적 계산 메소드
    changed = np.array(out_image, dtype=np.float64)
    changed[changed != -10000] -= minz
    changed[changed < 0] = 0
    changed[changed == -10000] = 0
    result = np.sum(np.abs(np.diff(changed, axis=1)), dtype=np.float64) * (gsd)  # 세로
    result += np.sum(np.abs(np.diff(changed, axis=0)), dtype=np.float64) * (gsd)  # 가로
    result += np.count_nonzero(changed) * (gsd * gsd)
    return result


def calculateVolume(inputGeoJson, referencesData, minz): # 체적 정보 계산 메소드, 위에 있는 3개 메소드를 사용하여 계산함
    transformResult = transform_coordinate(3857, int(referencesData.coordSystem),
                                           inputGeoJson[0]["coordinates"][0], "Polygon")
    inputGeoJson[0]['coordinates'][0] = transformResult
    try:
        if settings.DEV_LOCAL:
            dsm = os.path.split(settings.MEDIA_ROOT)[0] + referencesData.dsmDir
        else:
            dsm = 's3://droneplatform{}'.format(referencesData.dsmDir)

        with rasterio.Env(aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name="ap-northeast-2", AWS_S3_ENDPOINT='s3.ap-northeast-2.amazonaws.com'):
            with rasterio.open(dsm) as file:
                out_image, out_transform = mask(file, inputGeoJson, crop=True, nodata=-10000, filled=True)

        result = {"total": volume_by_bottom_total(out_image[0], minz, referencesData.gsd),
                  "fill": volume_by_bottom_fill(out_image[0], minz, referencesData.gsd),
                  "surface": surface_by_bottom(out_image[0], minz, referencesData.gsd)}
        result["cut"] = result["total"] - result["fill"]
        return result

    except FileNotFoundError as e:
        print(e)


def getLocation(inputLoc, referencesData): # 마우스 포인터 위치에 따른 Z값 계산 메소드 -  Maybe 2초 딜레이 설정되어 있음
    xmin = inputLoc[0]-0.001
    xmax = inputLoc[0]+0.001
    ymin = inputLoc[1]-0.001
    ymax = inputLoc[1]+0.001
    coord = [[[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]]
    geoJsonData = [{"type": "Polygon", "coordinates": coord}]

    transformResult = transform_coordinate(3857, int(referencesData.coordSystem), geoJsonData[0]["coordinates"][0],
                                           "Polygon")
    targetResult = transform_coordinate(3857, int(referencesData.coordSystem), [inputLoc[0], inputLoc[1]],
                                           "Point")
    geoJsonData[0]['coordinates'][0] = transformResult

    try:
        if settings.DEV_LOCAL:
            dsm = os.path.split(settings.MEDIA_ROOT)[0] + referencesData.dsmDir
        else:
            dsm = 's3://droneplatform{}'.format(referencesData.dsmDir)

        with rasterio.Env(aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name="ap-northeast-2", AWS_S3_ENDPOINT='s3.ap-northeast-2.amazonaws.com'):
            with rasterio.open(dsm) as file:
                out_image, out_transform = mask(file, geoJsonData, crop=True, all_touched=True, nodata=-10000)
        out_meta = file.meta
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
        dateToFileName = "".join(str(datetime.datetime.now()).replace(":", "").replace(".", "").split(" "))

        tmpSaveDir = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/processing/tmp".format(
            email=referencesData.email,
            projectId=referencesData.projectId)

        if not os.path.exists(tmpSaveDir):
            os.makedirs(tmpSaveDir)

        with rasterio.open(tmpSaveDir + "/" + dateToFileName + ".tif", "w", **out_meta) as dest:
            dest.write(out_image)
        with rasterio.open(tmpSaveDir + "/" + dateToFileName + ".tif", "r") as tmpRead:
            tmpReader = tmpRead.read(1)
        row, col = tmpRead.index(targetResult[0], targetResult[1])
        zLoc = -10000

        if col > len(tmpReader[row])-1:
            zLoc = -10000
        else:
            zLoc = tmpReader[row, col]
        os.remove(tmpSaveDir + "/" + dateToFileName + ".tif")
        return zLoc

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(e)
        return -10000


def getHighProfile(inputLoc, referencesData): # 직선 측정 - 종단면 확인 - 거리 프로파일 계산 메소드(매 1m 간격) + 다중 횡단 프로파일(횡단 거리 설정에 따른 여러개의 횡단 좌표 계산)
    polygon = [{"type": "Polygon", "coordinates": []}]
    x = []
    y = []
    for coord in inputLoc[0]["coordinates"]:
        x.append(coord[0])
        y.append(coord[1])
    x_changed = []
    y_changed = []
    transformResult = transform_coordinate(3857, int(referencesData.coordSystem), inputLoc[0]["coordinates"],
                                           "Polygon")
    for coord in transformResult:
        x_changed.append(coord[0])
        y_changed.append(coord[1])

    polygon[0]["coordinates"] = [[[min(x), min(y)], [min(x), max(y)], [max(x), max(y)],
                                  [max(x), min(y)], [min(x), min(y)]]]

    transformResult = transform_coordinate(3857, int(referencesData.coordSystem), polygon[0]["coordinates"][0],
                                           "Polygon")

    polygon[0]['coordinates'][0] = transformResult


    # interval = referencesData.gsd
    interval = 1
    # setting_length = 200
    setting_length = 10
    xDis = abs(abs(x_changed[0])-abs(x_changed[1]))
    yDis = abs(abs(y_changed[0])-abs(y_changed[1]))
    if xDis == 0:
        setting_length = int(yDis/interval)
    else:
        setting_length = int(xDis/interval)
    print(interval, xDis, yDis, math.sqrt(xDis*xDis+yDis*yDis), setting_length)
    try:
        if settings.DEV_LOCAL:
            dsm = os.path.split(settings.MEDIA_ROOT)[0] + referencesData.dsmDir
        else:
            dsm = 's3://droneplatform{}'.format(referencesData.dsmDir)

        with rasterio.Env(aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name="ap-northeast-2", AWS_S3_ENDPOINT='s3.ap-northeast-2.amazonaws.com'):
            with rasterio.open(dsm) as file:
                out_image, out_transform = mask(file, polygon, crop=True, all_touched=True, nodata=-10000)

        out_meta = file.meta
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
        tmpSaveDir = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/processing/tmp".format(
            email=referencesData.email,
            projectId=referencesData.projectId)
        if not os.path.exists(tmpSaveDir):
            os.makedirs(tmpSaveDir)
        dateToFileName = "".join(str(datetime.datetime.now()).replace(":", "").replace(".", "").split(" ")) + "11"

        with rasterio.open(tmpSaveDir + "/" + dateToFileName + ".tif", "w", **out_meta) as dest:
            dest.write(out_image)
        with rasterio.open(tmpSaveDir + "/" + dateToFileName + ".tif", "r") as tmpRead:
            tmpReader = tmpRead.read(1)
        z_value = []

        if x[0] == x[1]:  # 세로
            x_data = [x_changed[0]] * setting_length
            y_sort = sorted(y_changed)
            # y_data = np.linspace(y_sort[0], y_sort[1], setting_length)
            y_data = np.arange(y_changed[0], y_changed[1], interval if y_changed[0] < y_changed[1] else -interval)
        elif y[0] == y[1]:  # 가로
            y_data = [y_changed[0]] * setting_length
            x_sort = sorted(x_changed)
            # x_data = np.linspace(x_sort[0], x_sort[1], setting_length)
            x_data = np.arange(x_changed[0], x_changed[1], interval if x_changed[0] < x_changed[1] else -interval)
        else:
            m = float((y_changed[1] - y_changed[0]) / (x_changed[1] - x_changed[0]))
            n = float(y_changed[0] - (m * x_changed[0]))
            x_sort = sorted(x_changed)
            a = float(-1/m)
            b = -1
            c = -(a*x_changed[0]+b*y_changed[0])
            r1 = abs(interval*math.sqrt(a*a+b*b)-c+n)/(a-m)
            xDiff = abs(abs(x_changed[0])-abs(r1))




            # x_data = np.linspace(x_sort[0], x_sort[1], setting_length)
            x_data = np.arange(x_changed[0], x_changed[1], xDiff if x_changed[0] < x_changed[1] else -xDiff)
            print(x_sort[0], x_sort[1], interval)
            y_data = [m * num + n for num in x_data]


        for i in range(0, len(x_data) - 1):
            row, col = tmpRead.index(x_data[i], y_data[i])
            z_value.append(tmpReader[row, col])
        os.remove(tmpSaveDir + "/" + dateToFileName + ".tif")

        tmp_x_y = transform_coordinate(int(referencesData.coordSystem), 3857,
                                       [[x_data[i], y_data[i]] for i in range(len(x_data) - 1)], "Polygon")
        tmp_x = []
        tmp_y = []
        for coord in tmp_x_y:
            tmp_x.append(coord[0])
            tmp_y.append(coord[1])

        # return {"x": tmp_x, "y": tmp_y, "z": z_value, "interval": list(map(lambda x: x - x_sort[0], list(np.arange(x_sort[0], x_sort[1], interval)[:-1])))}
        return {"x": tmp_x, "y": tmp_y, "z": z_value, "interval": list(np.arange(0, math.sqrt(xDis*xDis+yDis*yDis), interval)[:-1])}
    except FileNotFoundError as e:
        print(e)
