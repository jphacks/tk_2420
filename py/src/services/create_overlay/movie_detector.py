import json
import logging
import os
import subprocess
import time
from collections import Counter
from env import PROCESSED_DATA_DIR

import cv2
import numpy as np
from ultralytics import YOLO

input_video_path = "Whiplash.mp4"
file_name = os.path.splitext(os.path.basename(input_video_path))[0]

json_output_path = f"py/overlays/{file_name}_overlay.json"
mp4_with_overlay_output_path = f"{file_name}_overlay.mp4"


logger = logging.getLogger(__name__)


def annotate_video(
    input_video_path: str,
    mp4_with_overlay_output_path: str,
    json_output_path: str,
    model_path: str,
    title: str 
) -> None:
    model = YOLO(model_path)
    cap = cv2.VideoCapture(input_video_path)

    display_window_while_processing = False

    fps = cap.get(cv2.CAP_PROP_FPS) or 30  # fpsが取得できない場合は30をデフォルトとする
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    tmp_movie_output_path = "./tmp.mp4"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(tmp_movie_output_path, fourcc, fps, (frame_width, frame_height))

    # 過去のバウンディングボックスとクラス情報を保存する辞書を初期化
    past_info: dict[int, dict] = {}
    # 前のフレームを保存する変数を初期化（シーン切り替え検出用）
    prev_frame_gray = None
    # シーン切り替えのしきい値
    scene_change_threshold = 30.0
    # Confidenceスコアのしきい値
    confidence_threshold = 0.40
    # 平滑化に使用するフレーム数
    smoothing_frames = 30
    fix_threshold = 0.85
    photo_info_counter = {
        "giselle": {"count": 0, "time": 0},
        "karina": {"count": 0, "time": 0},
        "ningning": {"count": 0, "time": 0},
        "winter": {"count": 0, "time": 0},
    }

    frame_count = 0

    # オーバーレイデータの初期化
    overlay_data: dict[str, list] = {"overlays": []}
    class_colors = {
        "karina": "#0000FF",  # ブルー
        "giselle": "#FF69B4",  # ピンク
        "winter": "#00FF00",  # グリーン
        "ningning": "#800080",  # パープル
    }
    class_names_dict = {"karina": 0, "giselle": 1, "winter": 2, "ningning": 3}
    for class_name in class_names_dict.keys():
        overlay_data["overlays"].append(
            {
                "id": class_name,
                "content": class_name,
                "color": class_colors.get(class_name, "#FFFFFF"),
                "fontSize": "16px",
                "lineColor": class_colors.get(class_name, "#FFFFFF"),
                "lineWidth": 2,
                "positions": [],
            }
        )

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_copy_for_photo = frame.copy()
        frame_count += 1
        current_time = round((frame_count - 1) / fps, 4)  # 時間を計算

        # シーン切り替えの検出
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_frame_gray is not None:
            diff = cv2.absdiff(prev_frame_gray, frame_gray)  # type: ignore
            non_zero_count = np.count_nonzero(diff)
            if non_zero_count / (frame_width * frame_height) * 100 > scene_change_threshold:
                # シーンが切り替わったと判断し、過去の情報をリセット
                past_info.clear()
        prev_frame_gray = frame_gray

        # 検出されたクラスを追跡
        detected_classes = set()

        # モデルによる検出とトラッキング
        results = model.track(frame, persist=True)

        for result in results:
            for box in result.boxes:
                # Confidenceスコアを取得
                confidence = box.conf.cpu().item()
                # バウンディングボックス座標とクラス情報を取得
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_id = int(box.cls.cpu().item())
                class_name = result.names[class_id]
                confidence_low_flag = False

                # トラッキングIDを取得
                tracking_id = int(box.id.cpu().item()) if box.id is not None else None

                # クラス名に応じて色を設定
                hex_color = class_colors.get(class_name, "#FFFFFF")
                color = tuple(int(hex_color.lstrip("#")[i : i + 2], 16) for i in (4, 2, 0))

                if tracking_id is not None:
                    # 該当IDの過去の情報を初期化または取得
                    if tracking_id not in past_info:
                        past_info[tracking_id] = {
                            "bboxes": [],
                            "class_names": [],
                            "confidences": [],
                            "fixed_class_name": None,
                        }

                    # 現在の情報を保存
                    past_info[tracking_id]["bboxes"].append([x1, y1, x2, y2])
                    past_info[tracking_id]["class_names"].append(class_name)
                    past_info[tracking_id]["confidences"].append(confidence)

                    # 保存するフレーム数を制限
                    if len(past_info[tracking_id]["bboxes"]) > smoothing_frames:
                        past_info[tracking_id]["bboxes"].pop(0)
                        past_info[tracking_id]["class_names"].pop(0)
                        past_info[tracking_id]["confidences"].pop(0)

                    # 過去のbboxから平均座標を計算
                    num_bboxes = len(past_info[tracking_id]["bboxes"])
                    x1_smooth = int(sum(b[0] for b in past_info[tracking_id]["bboxes"]) / num_bboxes)
                    y1_smooth = int(sum(b[1] for b in past_info[tracking_id]["bboxes"]) / num_bboxes)
                    x2_smooth = int(sum(b[2] for b in past_info[tracking_id]["bboxes"]) / num_bboxes)
                    y2_smooth = int(sum(b[3] for b in past_info[tracking_id]["bboxes"]) / num_bboxes)

                    if past_info[tracking_id]["fixed_class_name"] is None and confidence < confidence_threshold:
                        confidence_low_flag = True

                    if past_info[tracking_id]["fixed_class_name"] is not None:
                        # 固定されたクラス名を使用
                        class_name = past_info[tracking_id]["fixed_class_name"]

                    # 一度Confidenceが0.9を超えた場合、固定されたクラス名を使用
                    if confidence >= fix_threshold and past_info[tracking_id]["fixed_class_name"] is None:
                        past_info[tracking_id]["fixed_class_name"] = class_name
                    else:
                        class_counter = Counter(past_info[tracking_id]["class_names"])
                        most_common_class_name, _ = class_counter.most_common(1)[0]
                        class_name = most_common_class_name

                # 画像を保存
                save_photo(
                    frame_copy_for_photo, frame_width, frame_height, x1, y1, x2, y2, class_name, photo_info_counter, title
                )

                if not confidence_low_flag and tracking_id is not None:
                    # y1_smoothの調整（past_infoには影響しない）
                    adjusted_y1_smooth = y1_smooth
                    if y1_smooth - 5 < 0:
                        adjusted_y1_smooth += 15
                    # バウンディングボックスを描画
                    cv2.line(frame, (x1_smooth, adjusted_y1_smooth), (x2_smooth, adjusted_y1_smooth), color, 2)

                    # ラベルを描画
                    label_text = f"{class_name}"
                    cv2.putText(
                        frame,
                        label_text,
                        (x1_smooth, adjusted_y1_smooth - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        1,
                        cv2.LINE_AA,
                    )

                    # オーバーレイデータに追加
                    if class_name in class_names_dict:
                        position = {
                            "time": current_time,
                            "startX": x1_smooth,
                            "startY": adjusted_y1_smooth,
                            "endX": x2_smooth,
                            "endY": y2_smooth,
                            "visible": True,
                        }
                        overlay_data["overlays"][class_names_dict[class_name]]["positions"].append(position)
                        detected_classes.add(class_name)

        # 検出されなかったクラスのvisibleをfalseに設定
        for class_name in class_names_dict:
            if class_name not in detected_classes:
                position = {"time": current_time, "startX": 0, "startY": 0, "endX": 0, "endY": 0, "visible": False}
                overlay_data["overlays"][class_names_dict[class_name]]["positions"].append(position)

        # フレームを書き込み
        out.write(frame)

        if display_window_while_processing:
            cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # オーバーレイデータをresult.jsonに保存
    with open(json_output_path, "w") as f:
        json.dump(overlay_data, f, indent=2)

    # 音声を含めて動画を保存
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            tmp_movie_output_path,
            "-i",
            input_video_path,
            "-c:v",
            "libx264",
            "-c:a",
            "copy",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-y",
            mp4_with_overlay_output_path,
        ]
    )

    os.remove(tmp_movie_output_path)


def save_photo(frame, frame_width, frame_height, x1, y1, x2, y2, class_name, photo_info_counter, video_title):
    os.makedirs(f"{PROCESSED_DATA_DIR}/oshi_photos/{video_title}", exist_ok=True)
    os.makedirs(f"{PROCESSED_DATA_DIR}/oshi_photos/{video_title}/{class_name}", exist_ok=True)
    frame_area = frame_width * frame_height
    box_area = abs(x2 - x1) * abs(y2 - y1)
    # 推しがアップの場合 or 中央にいる場合保存する
    if box_area / frame_area > 0.5 or (
        (x1 < frame_width / 2 and x2 > frame_width / 2)
        or (y1 < frame_height / 2 and y2 > frame_height / 2)
        and box_area / frame_area > 0.3
    ):
        if time.time() - photo_info_counter[class_name]["time"] < 2:
            return
        photo_info_counter[class_name]["count"] += 1
        photo_info_counter[class_name]["time"] = time.time()
        output_path = f"{PROCESSED_DATA_DIR}/oshi_photos/{video_title}/{class_name}/{photo_info_counter[class_name]['count']}.png"
        cv2.imwrite(output_path, frame)


if __name__ == "__main__":
    annotate_video(input_video_path, mp4_with_overlay_output_path, json_output_path)
