# アノテーションの可視化処理

import cv2
import numpy as np
from random import randint

# 画像の読み込み
img = cv2.imread('./tmp/giselle1.jpg')
h, w = img.shape[:2]

# アノテーションの読み込み
with open('./tmp/giselle1.txt', 'r') as f:
    labels = f.read().splitlines()

# 各アノテーションを描画
for label in labels:
    class_id, *poly = label.split(' ')

    poly = np.asarray(poly, dtype=np.float16).reshape(-1, 2)  # Read poly, reshape
    poly *= [w, h]  # Unscale

    # ランダムな色でポリゴンを描画
    cv2.polylines(img, [poly.astype('int')], True, (randint(0, 255), randint(0, 255), randint(0, 255)), 2)  # 線の太さは2に調整

# 画像の表示
cv2.imshow("Annotated Image", img)

# キー入力待機
cv2.waitKey(0)
cv2.destroyAllWindows()
