import face_recognition
import cv2
import numpy as np
import glob
import subprocess
import os

# 入力動画と出力パス
video_path = "Whiplash.mp4"
output_path = "output.mp4"

# 各人物の画像パスパターンと名前のリスト
face_images_patterns = {
    "giselle": "../aespa_dataset/giselle/giselle[1-9].jpg",
    "karina": "../aespa_dataset/karina/karina[1-9].jpg",
    "ningning": "../aespa_dataset/ningning/ningning[1-9].jpg",
    "winter": "../aespa_dataset/winter/winter0[1-9].jpg"
}

# 各人物の顔エンコーディングを保存するリスト
known_face_encodings = []
known_face_names = []

# 各人物の全画像からエンコーディングを取得して平均化
for name, pattern in face_images_patterns.items():
    encodings = []
    found_images = glob.glob(pattern)
    if not found_images:
        print(f"Error: No images found for pattern {pattern}. Please check the file path.")
        continue

    for image_path in found_images:
        print(f"Loading image: {image_path}")
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if face_encodings:
            encodings.append(face_encodings[0])
        else:
            print(f"Warning: No face found in {image_path}")

    # 各人物のエンコーディングが1つ以上取得できた場合、平均を計算
    if encodings:
        mean_encoding = np.mean(encodings, axis=0)
        known_face_encodings.append(mean_encoding)
        known_face_names.append(name)
        print(f"Added encoding for {name}")
    else:
        print(f"Warning: No faces found for {name} in any of the images.")

# 動画の設定
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Unable to open video file {video_path}")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 出力動画の設定
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from video.")
        break

    # 50%にフレームをリサイズ
    frame = cv2.resize(frame, (frame_width, frame_height))
    rgb_frame = frame[:, :, ::-1]

    import time
    time.sleep(0.5)
    # 顔の位置を取得して存在を確認
    face_locations = face_recognition.face_locations(rgb_frame)
    if not face_locations:
        print("No faces detected in this frame. Skipping frame.")
        out.write(frame)
        continue

    # 顔のエンコーディングを取得
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=1)
    if not face_encodings:
        print("Face encoding failed. Skipping frame.")
        out.write(frame)
        continue

    # 顔認識の結果を描画
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # 出力動画にフレームを書き込む
    out.write(frame)



cap.release()
out.release()

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
