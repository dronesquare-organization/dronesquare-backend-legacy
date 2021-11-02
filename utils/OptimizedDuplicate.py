from imgs.models import Imgs


def optimizeDuplicate(params):
    import os
    import cv2
    import numpy as np

    path, imgList, email, projectId = params
    List_of_SelectedImg = []
    # MdisAve_t = []
    flagNext = 1
    cnt = 0
    for imgN in imgList:
        img_path = os.path.join(path, imgN)
        if not img_path.endswith(('.JPG', '.jpg', '.PNG', '.png')):
            continue

        cnt = cnt + 1
        #    print("{} ".format(cnt))

        if flagNext == 1:
            n = np.fromfile(img_path, np.uint8)
            im1 = cv2.imdecode(n, cv2.IMREAD_COLOR)
            im1_G = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
            flagNext = 2
            List_of_SelectedImg.append(imgN)
            continue

        n = np.fromfile(img_path, np.uint8)
        im2 = cv2.imdecode(n, cv2.IMREAD_COLOR)
        im2_G = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

        # 3. matching key points
        Max_Features = 100
        Thresh_Mdis = 70
        # Good_match_percent = 0.5

        # 3.1 detect orb features and compute descriptors
        orb = cv2.ORB_create(Max_Features)
        keypoints1, descriptors1 = orb.detectAndCompute(im1_G, None)
        keypoints2, descriptors2 = orb.detectAndCompute(im2_G, None)

        # 3.2 match features
        matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)

        # 3.3 Validation
        Mdis = []
        for i in range(0, len(matches)):
            # print(cnt, ":", i)
            Mdis.append(matches[i].distance)

        MdisAve = np.average(Mdis)
        #    MdisAve_t.append(MdisAve)

        # 3.4 Select images with the optimal overlapping rate
        if MdisAve > Thresh_Mdis:
            im1 = im2
            im1_G = im2_G
            List_of_SelectedImg.append(imgN)
            continue

    # 4. save the list of images selected
    List_of_SelectedImg = np.array(List_of_SelectedImg)
    for name in List_of_SelectedImg:
        img = Imgs.objects.filter(email=email, projectId=projectId, name=name.split(".")[0], format=name.split(".")[1])
        if img is not None:
            img.update(isOptimized=True)
