# -*- coding: utf-8 -*-
import os
import cv2
import numpy as np
import boto3
from backendAPI import settings


def adjust_gamma(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array(
        [((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]
    ).astype("uint8")

    return cv2.LUT(image, table)


# brightness
def adjust_brightness_increase(image, delta_brightness):
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cols, rows = img_gray.shape
    gamma = 1.0
    gamma_step = 0.1

    curr_brightness = np.sum(img_gray) / (255 * cols * rows)
    target_brightness = curr_brightness + delta_brightness
    new_img = img_gray

    # cnt =0
    while True:
        # cnt = cnt +1
        brightness = np.sum(new_img) / (255 * cols * rows)
        if brightness >= target_brightness:
            break

        gamma += gamma_step
        new_img = adjust_gamma(img_gray, gamma)

    # print("iteration: {} & gamma: {}".format(cnt, gamma))
    new_img = adjust_gamma(image, gamma)
    return new_img


# darkness
def adjust_brightness_decrease(image, delta_brightness):
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cols, rows = img_gray.shape
    gamma = 1.0
    gamma_step = 0.1

    curr_brightness = np.sum(img_gray) / (255 * cols * rows)
    target_brightness = curr_brightness - delta_brightness
    new_img = img_gray

    # cnt =0
    while True:
        # cnt = cnt +1
        brightness = np.sum(new_img) / (255 * cols * rows)
        if brightness <= target_brightness:
            break

        gamma -= gamma_step
        new_img = adjust_gamma(img_gray, gamma)

    # print("iteration: {} & gamma: {}".format(cnt, gamma))
    new_img = adjust_gamma(image, gamma)
    return new_img


def change_filter(originFile, delta, img):
    # n = np.fromfile(originFile, np.uint8)
    # img_original = cv2.imdecode(n, cv2.IMREAD_COLOR)

    # if delta >= 0:
    #     img_original = adjust_brightness_increase(img_original, abs(delta))
    # else:
    #     img_original = adjust_brightness_decrease(img_original, abs(delta))
    # destination = settings.MEDIA_ROOT + '/{email}/projects/{projectId}/bright'.format(email=img.email,
    #                                                                                   projectId=img.projectId)
    # if not os.path.exists(destination):
    #     os.makedirs(destination)
    # cv2.imwrite(destination+'/'+img.name, img_original)

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    file = s3_client.get_object(Bucket="droneplatform", Key=originFile)["Body"].read()
    img_original = cv2.imdecode(np.asarray(bytearray(file)), cv2.IMREAD_COLOR)

    if delta >= 0:
        img_original = adjust_brightness_increase(img_original, abs(delta))
    else:
        img_original = adjust_brightness_decrease(img_original, abs(delta))
    destination = "media/{email}/projects/{projectId}/bright/{name}".format(
        email=img.email,
        projectId=img.projectId,
        name="filtered_" + str(img.fileDir).split("/")[-1],
    )
    if not os.path.exists("/home/ubuntu/" + "/".join(destination.split("/")[:-1])):
        os.makedirs("/home/ubuntu/" + "/".join(destination.split("/")[:-1]))

    cv2.imwrite("/home/ubuntu/" + destination, img_original)

    s3_client.upload_file(
        "/home/ubuntu/" + destination,
        "droneplatform",
        destination,
        {"CacheControl": "no-cache, no-store, must-revalidate"},
    )
    os.remove("/home/ubuntu/" + destination)

    return img_original
