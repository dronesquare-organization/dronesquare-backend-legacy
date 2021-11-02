import os
import cv2
import numpy as np

import statistics
import random

def IOR_F(Img_path):
    Thresh_totalnum_imgs = 10 #1.the total number of images should be more than 10
    num_selectedimgs_rate = 0.1#0.05 #5%


    #[1]  select images
    num_img = len(os.listdir(Img_path))

    num_selectedimg = int(num_img*num_selectedimgs_rate)
    if num_selectedimg > 200:
        num_selectedimg = 200
    elif num_selectedimg < 5:
        num_selectedimg = 5

    Thresh_num_ORimgs = int(num_selectedimg*0.5) #2. the number of image pairs with the proper overlapping rate

    if num_img < Thresh_totalnum_imgs:
        print('The total number of images is too low: {} images'.format(num_img))
        return 0, 0

    saveidx = []
    cnt =0
    loopstop = 0

    while loopstop == 0:
        cnt += 1
        selectedidx = random.randrange(0, (num_img-2))

        if cnt > num_selectedimg:
            loopstop = 1
            continue

        saveidx.append(selectedidx)

    saveidx = np.array(saveidx)
    saveidx = sorted(saveidx) #ascending order

    #[2] loading images
    #import image names
    list_img = []
    for imgN in os.listdir(Img_path):
        list_img.append(imgN)

    # loading images w.r.t. saveidx list
    arrayimg1 = []
    arrayimg2 = []

    num_selectedimg = 2
    for i in range(num_selectedimg):
        idx1 = saveidx[i]
        idx2 = idx1 + 1

        imgN1 = list_img[idx1]
        imgN2 = list_img[idx2]

        img1_path = os.path.join(Img_path, imgN1)
        img2_path = os.path.join(Img_path, imgN2)

        if not img1_path.endswith(('.JPG','.jpg')):
            continue
        if not img2_path.endswith(('.JPG','.jpg')):
            continue


        n1 = np.fromfile(img1_path, np.uint8)
        a1 = cv2.imdecode(n1, cv2.IMREAD_COLOR)

        n2 = np.fromfile(img2_path, np.uint8)
        a2 = cv2.imdecode(n2, cv2.IMREAD_COLOR)

        #reduce image size
        if i == 0:
            imgH, imgW, channels = a1.shape
            dim_size = (int(imgW/4.0), int(imgH/4.0)) #width, height

        img1 = cv2.resize(a1, dim_size, interpolation=cv2.INTER_AREA)
        img2 = cv2.resize(a2, dim_size, interpolation=cv2.INTER_AREA)

        arrayimg1.append(img1) #height, width
        arrayimg2.append(img2)


    #[3] registration(key points)
    sift = cv2.xfeatures2d.SIFT_create()

    ratio = 0.5 #for matching distance 0.85
    thresh_min_match_rate = 0.5 #5%
    min_match = 10
    OVR_array =[]

    num_selectedimg = len(arrayimg1)
    print('Number of image pair: {}\n'.format(num_selectedimg))

    num_unOR = 0
    imgH, imgW, channels = arrayimg1[0].shape #resized images
    for i in range(num_selectedimg):
        print('index: {}'.format(i+1))
        img1 = arrayimg1[i]
        img2 = arrayimg2[i]
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        matcher = cv2.BFMatcher()
        raw_matches = matcher.knnMatch(des1, des2, k=2)

        good_points = []

        for m1, m2 in raw_matches:
            if m1.distance < ratio * m2.distance:
                good_points.append((m1.trainIdx, m1.queryIdx))

        match_rate = ((len(good_points))/(len(raw_matches)))*100

        if match_rate > thresh_min_match_rate and len(good_points) > min_match:
            image1_kp = np.float32([kp1[i].pt for (_, i) in good_points])
            image2_kp = np.float32([kp2[i].pt for (i, _) in good_points])
            H, status = cv2.findHomography(image2_kp, image1_kp, cv2.RANSAC, 5.0)       #img2 to img1(refer)
            Hinv, statusinv = cv2.findHomography(image1_kp, image2_kp, cv2.RANSAC, 5.0) #img1 to img2(refer)
        else:
            num_unOR += 1
            continue

        # total image size
        height_panorama = imgH*2
        width_panorama = imgW*2

        if np.shape(H) == () or np.size(H) == 0:
            num_unOR += 1
            continue


        print(" img2 ", img2)
        print(" H ", H)
        print(" width_panorama ", width_panorama)
        print(" height_panorama ", height_panorama)
        # projection
        val_pano2 = cv2.warpPerspective(img2, H, (width_panorama, height_panorama)) #img2 to img1
        val_pano1 = cv2.warpPerspective(img1, Hinv, (width_panorama, height_panorama)) #img1 to img2

        #count pixel with non-zero value
        val_pano2_t = np.array(val_pano2)
        cnt2 = val_pano2_t.any(axis=-1).sum() #4474569/4990464

        val_pano1_t = np.array(val_pano1)
        cnt1 = val_pano1_t.any(axis=-1).sum() #4846995/4990464

        #generate each aligned image
        if cnt2 > cnt1: #reference: img1, target: img2
            panorama1 = np.zeros((height_panorama, width_panorama, 3)) #initialization
            panorama1[0:img1.shape[0], 0:img1.shape[1], :] = img1  #allocation img1
            panorama2 = val_pano2
            panorama1 = panorama1.astype(np.uint8)
        else: #reference: img2, target: img1
            panorama2 = np.zeros((height_panorama, width_panorama, 3)) #initialization
            panorama2[0:img2.shape[0], 0:img2.shape[1], :] = img2  #allocation img2
            panorama1 = val_pano1
            panorama2 = panorama2.astype(np.uint8)

        #convert rgb to gray
        panorama1Gray = cv2.cvtColor(panorama1, cv2.COLOR_BGR2GRAY)
        panorama2Gray = cv2.cvtColor(panorama2, cv2.COLOR_BGR2GRAY)

        #reduce image up to 1/8
        imgH_t, imgW_t = panorama1Gray.shape
        dim_size = (int(imgW_t/8.0), int(imgH_t/8.0))
        R_panorama1 = cv2.resize(panorama1Gray, dim_size, interpolation=cv2.INTER_AREA)
        R_panorama2 = cv2.resize(panorama2Gray, dim_size, interpolation=cv2.INTER_AREA)

        #[6] detect overlapping area
        totalcnt = 0
        cnt_ov =0
        for irow in range(dim_size[1]):
            for icol in range(dim_size[0]):
                pixelV1 = R_panorama1[irow,icol]
                pixelV2 = R_panorama2[irow,icol]

                if pixelV1 > 0:
                    totalcnt += 1

                if pixelV1 > 0 and pixelV2 > 0:
                    cnt_ov += 1

        #[7] calculate overlapping rate
        OverlapRate = (cnt_ov/totalcnt)*100
        OVR_array.append(OverlapRate)


    if num_unOR == num_selectedimg:
        print('Image overlapping is totally wrong\n')
        return -1,-1

    #[8] calculate average overlapping rate
    OVR_array = np.array(OVR_array)
    average_OR = OVR_array.mean()
    std_OVR = statistics.stdev(OVR_array)

    print("Done IORE")
    return average_OR, std_OVR
