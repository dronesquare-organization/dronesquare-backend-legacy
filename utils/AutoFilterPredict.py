import cv2
import numpy as np


def IE(img, model):
    newW = 256
    newH = 170
    Y_class = [0.8, 1.0, 1.2, 1.5, 1.7, 2.0]
    a = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    new_a = [cv2.resize(a, (newW, newH))]
    X_Img = np.array(new_a) / 255.
    NNpreds = model.predict(X_Img)
    predict_class = np.argmax(NNpreds, axis=1)
    predict_class = predict_class.tolist()
    return round((Y_class[predict_class[0]] - 1.0)/10, 3)  # <- DB 저장
