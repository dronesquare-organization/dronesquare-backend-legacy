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

        if flagNext == 1: # 가장 처음 이미지 리드용 로직
            n = np.fromfile(img_path, np.uint8) # 구성한 이미지 패스에 따라서 이미지 파일 리드
            im1 = cv2.imdecode(n, cv2.IMREAD_COLOR) # 첫번째 이미지 리드 - 읽어온 이미지 파일을 바이너리 형태로 디코딩, Byte 단위
            im1_G = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY) # 첫번째 이미지 리드 - BGR에서 Gray-scale로 컨버팅
            flagNext = 2
            List_of_SelectedImg.append(imgN) # 현재 이미지를 리스트에 저직
            continue # 이후 로직 스킵

        n = np.fromfile(img_path, np.uint8) # 구성한 이미지 패스를 따라서 이미지 파일 다시 리드
        im2 = cv2.imdecode(n, cv2.IMREAD_COLOR) # 두번째 이미지 리드 - 읽어온 이미지 파일을 바리너리 형태로 디코딩, Byte 단위
        im2_G = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY) # 두번째 이미지 리드 - BGR에서 Grey-scale로 컨버팅

        # 3. matching key points
        Max_Features = 100
        Thresh_Mdis = 70
        # Good_match_percent = 0.5

        # 3.1 detect orb features and compute descriptors
        orb = cv2.ORB_create(Max_Features)
        keypoints1, descriptors1 = orb.detectAndCompute(im1_G, None) # 첫번째 이미지 특징점 계산
        keypoints2, descriptors2 = orb.detectAndCompute(im2_G, None) # 두번째 이미지 특징점 계산

        # 3.2 match features
        matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_BRUTEFORCE_HAMMING) # 특징 매칭(Feature Matching) 객체 생성
        matches = matcher.match(descriptors1, descriptors2, None) # 두 특징점 특징점 매칭 진행

        # 3.3 Validation
        Mdis = []
        for i in range(0, len(matches)):
            # print(cnt, ":", i)
            Mdis.append(matches[i].distance)

        MdisAve = np.average(Mdis) # 측정된 특징 매칭 수치를 평균화
        #    MdisAve_t.append(MdisAve)

        # 3.4 Select images with the optimal overlapping rate
        if MdisAve > Thresh_Mdis: # 측정한 특징 매칭 평균값이 70이상일 경우 현재 이미지를 리스트에 추가
            im1 = im2 # 비교할 이미지를 변경 - 두번째로 리드한 이미지가 다음 반복문 동작에서 비교 대상이 되는 이미지 파일로 사용
            im1_G = im2_G
            List_of_SelectedImg.append(imgN) # 현재 이미지를 선택된 이미지 리스트에 추가
            continue

    # 4. save the list of images selected
    List_of_SelectedImg = np.array(List_of_SelectedImg)
    for name in List_of_SelectedImg:
        img = Imgs.objects.filter(email=email, projectId=projectId, name=name.split(".")[0], format=name.split(".")[1])
        if img is not None:
            img.update(isOptimized=True)
