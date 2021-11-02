# -*- coding: utf-8 -*-

import rasterio
from pyproj import Transformer
from rasterio.mask import mask
import numpy as np
import os
import datetime
from utils.Calculate3D import transform_coordinate
import json
from backendAPI import settings
import boto3

def findFromVoxel(inputLoc, referencesData):
    geoJsonData = [{"type": "Point", "coordinates": inputLoc}]

    transformResult = transform_coordinate(3857, int(referencesData.coordSystem), geoJsonData[0]["coordinates"],
                                           "Point")
    geoJsonData[0]['coordinates'] = transformResult

    try:
        if settings.DEV_LOCAL:
            dsm = os.path.split(settings.MEDIA_ROOT)[0] + referencesData.dsmDir
        else:
            dsm = 's3://droneplatform/{}'.format(referencesData.dsmDir)

        with rasterio.Env(AWS_S3_ENDPOINT='s3.ap-northeast-2.amazonaws.com'):
            with rasterio.open(dsm) as file:
                out_image, out_transform = mask(file, geoJsonData, crop=True, all_touched=True)

        out_meta = file.meta
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
        dateToFileName = "".join(str(datetime.datetime.now()).replace(":", "").replace(".", "").split(" "))+"44"

        tmpSaveDir = settings.MEDIA_ROOT + "/{email}/projects/{projectId}/processing/tmp".format(
            email=referencesData.email,
            projectId=referencesData.projectId)

        if not os.path.exists(tmpSaveDir):
            os.makedirs(tmpSaveDir)

        with rasterio.open(tmpSaveDir + "/" + dateToFileName + ".tif", "w", **out_meta) as dest:
            dest.write(out_image)
        with rasterio.open(tmpSaveDir + "/" + dateToFileName + ".tif", "r") as tmpRead:
            tmpReader = tmpRead.read(1)
        row, col = tmpRead.index(transformResult[0], transformResult[1])
        z_value = tmpReader[row, col]
        if z_value == -10000:
            z_value = 0

        if settings.DEV_LOCAL:
            voxelDir = dsm = os.path.split(settings.MEDIA_ROOT)[0] + referencesData.voxelDir

            with open(voxelDir) as json_file:
                json_data = json.load(json_file)
                json_minimum = json_data["minimum"] # y x z
                json_size = json_data["size"] # 간격
                number = json_data["number"] # y x z
                json_object = json_data["data"]
        else:
            BUCKET_NAME = 'droneplatform'
            s3 = boto3.resource('s3')


            obj = s3.Object(BUCKET_NAME, referencesData.voxelDir)
            data = obj.get()['Body'].read().decode('utf-8')
            json_data = json.loads(data)

            json_minimum = json_data["minimum"] # y x z
            json_size = json_data["size"] # 간격
            number = json_data["number"] # y x z
            json_object = json_data["data"]

        y = float(json_minimum.split(" ")[0])
        x = float(json_minimum.split(" ")[1])
        z = float(json_minimum.split(" ")[2])
        y_num = int(number.split(" ")[0])
        x_num = int(number.split(" ")[1])
        z_num = int(number.split(" ")[2])
        x_key = str(int((geoJsonData[0]['coordinates'][0]-x)/float(json_size)))
        y_key = str(int((geoJsonData[0]['coordinates'][1]-y)/float(json_size)))
        z_key = str(int((z_value-z)/float(json_size)))

        if(x_num <= int(x_key)):
            return "empty"
        if(y_num <= int(y_key)):
            return "empty"
        if(z_num <= int(z_key)):
            return "empty"

        os.remove(tmpSaveDir + "/" + dateToFileName + ".tif")
        if y_key in json_object.keys():
            if x_key in json_object[y_key].keys():
                if z_key in json_object[y_key][x_key].keys():
                    print(json_object[y_key][x_key][z_key])
                    return json_object[y_key][x_key][z_key]
                else:
                    keys = list(json_object[y_key][x_key].keys())
                    if len(keys) == 0:
                        return "empty"
                    else:
                        return json_object[y_key][x_key][keys[0]]
            else:
                return "empty"
        else:
            return "empty"

        
        # return tmpReader[row, col]

    except FileNotFoundError as e:
        print(e)