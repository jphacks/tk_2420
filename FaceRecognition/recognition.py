import face_recognition
import cv2
import numpy as np
import os
import glob
import subprocess

# 入力動画と出力パス
video_path = "Whiplash.mp4"
output_path = "output.mp4"

# 各人物の画像パスパターンと名前のリスト
face_images_patterns = {
    "giselle": "../aespa_dataset/giselle/giselle*.jpg",
    "karina": "../aespa_dataset/karina/karina*.jpg",
    "ningning": "../aespa_dataset/ningning/ningning*.jpg",
    "winter": "../aespa_dataset/winter/winter*.jpg"
}

known_face_encodings = []
known_face_names = []

# 各人物の全画像からエンコーディングを取得して平均化
for name, pattern in face_images_patterns.items():
    encodings = []
    for image_path in glob.glob(pattern):
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            encodings.append(face_encodings[0])

    # 各人物のエンコーディングが1つ以上取得できた場合、平均を計算
    if encodings:
        mean_encoding = np.mean(encodings, axis=0)
        known_face_encodings.append(mean_encoding)
        known_face_names.append(name)
    else:
        print(f"Warning: No faces found for {name} in the given images.")

# 動画の設定
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 出力動画の設定
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # フレームのRGB変換と顔位置・エンコーディングの取得
    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # 認識結果をフレームに描画
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # 一致する顔が見つかった場合の名前取得
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        # 名前と顔の矩形を描画
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # フレームを出力と表示
    out.write(frame)
    cv2.imshow("Frame", frame)

    # 'q'キーで終了
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# リソース解放
cap.release()
out.release()
cv2.destroyAllWindows()

# 音声付きで最終出力に変換
final_output_path = "Whiplash_face_recognition.mp4"
subprocess.run([
    "ffmpeg",
    "-i", output_path,
    "-i", video_path,
    "-c", "copy",
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-y", final_output_path,
])

# 中間ファイルの削除
os.remove(output_path)
