# 必要なライブラリのインポート
import cv2
from deepface import DeepFace
from deep_sort_realtime.deepsort_tracker import DeepSort
import numpy as np

# モデルと検出器の設定
model_name = 'Facenet'  # 使用する顔認識モデル（VGG-Face, Facenet, OpenFace, DeepFaceなど）
detector_backend = 'mtcnn'  # 顔検出のバックエンド（opencv, mtcnn, retinafaceなど）

# 動画の読み込み
video_path = 'input_video.mp4'  # 入力動画のパスを指定
cap = cv2.VideoCapture(video_path)

# Deep SORTトラッカーの初期化
tracker = DeepSort(max_age=30, n_init=3, max_cosine_distance=0.3)

# フォント設定
font = cv2.FONT_HERSHEY_SIMPLEX

# フレームサイズの取得
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 出力動画の設定（必要に応じて）
output_path = 'output_video.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, 30.0, (frame_width, frame_height))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # フレームのコピーを作成
    draw_frame = frame.copy()

    # 顔検出と顔認識
    try:
        # 顔検出
        detections = DeepFace.extract_faces(
            img_path=frame,
            target_size=(224, 224),
            detector_backend=detector_backend,
            enforce_detection=False
        )
    except:
        detections = []

    bbox_xywh = []
    confidences = []
    class_ids = []

    for face in detections:
        # バウンディングボックスの取得
        x, y, w, h = face['facial_area'].values()
        face_img = frame[y:y+h, x:x+w]

        # 顔認識
        try:
            result = DeepFace.find(
                img_path=face_img,
                db_path='dataset/',  # データセットのパス
                model_name=model_name,
                detector_backend=detector_backend,
                enforce_detection=False
            )
            if len(result) > 0:
                identity = result[0]['identity'].values[0]
                name = identity.split('/')[-2]  # フォルダ名を人物名として使用
            else:
                name = 'Unknown'
        except:
            name = 'Unknown'

        # バウンディングボックスと信頼度の追加
        bbox_xywh.append([x, y, w, h])
        confidences.append(0.99)  # 仮の信頼度を設定
        class_ids.append(name)

    # トラッカーへの入力データを準備
    if len(bbox_xywh) > 0:
        outputs = tracker.update_tracks(bbox_xywh, confidences, class_ids, frame=frame)

        # 結果の描画
        for track in outputs:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            ltrb = track.to_ltrb()  # 左、上、右、下の座標
            x1, y1, x2, y2 = map(int, ltrb)
            name = track.get_det_class()

            # バウンディングボックスとラベルの描画
            cv2.rectangle(draw_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f'{name} ID:{track_id}'
            cv2.putText(draw_frame, label, (x1, y1 - 10), font, 0.6, (0, 255, 0), 2)
    else:
        # 検出がない場合もトラッカーを更新
        tracker.increment_ages()

    # フレームの表示
    cv2.imshow('Face Recognition and Tracking', draw_frame)

    # 出力動画の書き込み（必要に応じて）
    out.write(draw_frame)

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースの解放
cap.release()
out.release()
cv2.destroyAllWindows()
