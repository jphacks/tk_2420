import cv2
from ultralytics import YOLO
import subprocess
import os
import logging
import numpy as np

input_video_path = "../Whiplash.mp4"
output_path = "../output.mp4"

logger = logging.getLogger(__name__)

def annotate_video(input_video_path:str, output_path:str, model_path: str = "../models/hackv4i_yolo11x.pt") -> None:
    model = YOLO(model_path)
    cap = cv2.VideoCapture(input_video_path)

    display_window_while_processing = False

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    tmp_output_path = "./tmp.mp4"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(tmp_output_path, fourcc, fps, (frame_width, frame_height))

    # 過去のバウンディングボックスとクラス情報を保存する辞書を初期化
    past_info = {}
    # 前のフレームを保存する変数を初期化（シーン切り替え検出用）
    prev_frame_gray = None
    # シーン切り替えのしきい値
    scene_change_threshold = 30.0
    # Confidenceスコアのしきい値
    confidence_threshold = 0.5
    # 平滑化に使用するフレーム数
    smoothing_frames = 30

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # シーン切り替えの検出
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_frame_gray is not None:
            diff = cv2.absdiff(prev_frame_gray, frame_gray)
            non_zero_count = np.count_nonzero(diff)
            if non_zero_count / (frame_width * frame_height) * 100 > scene_change_threshold:
                # シーンが切り替わったと判断し、過去の情報をリセット
                past_info.clear()
        prev_frame_gray = frame_gray

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

                # トラッキングIDを取得
                tracking_id = int(box.id.cpu().item()) if box.id is not None else None

                # クラス名に応じて色を設定
                if class_name == "karina":  # ブルー
                    color = (255, 0, 0)
                elif class_name == "giselle":  # ピンク
                    color = (255, 105, 180)
                elif class_name == "winter":  # グリーン
                    color = (0, 255, 0)
                elif class_name == "ningning":  # パープル
                    color = (128, 0, 128)
                else:
                    color = (255, 255, 255)  # デフォルトの色

                if tracking_id is not None:
                    # 該当IDの過去の情報を初期化または取得
                    if tracking_id not in past_info:
                        past_info[tracking_id] = {
                            'bboxes': [],
                            'class_names': [],
                            'confidences': []
                        }

                    # 現在の情報を保存
                    past_info[tracking_id]['bboxes'].append([x1, y1, x2, y2])
                    past_info[tracking_id]['class_names'].append(class_name)
                    past_info[tracking_id]['confidences'].append(confidence)

                    # 保存するフレーム数を制限
                    if len(past_info[tracking_id]['bboxes']) > smoothing_frames:
                        past_info[tracking_id]['bboxes'].pop(0)
                        past_info[tracking_id]['class_names'].pop(0)
                        past_info[tracking_id]['confidences'].pop(0)

                    # 過去のbboxから平均座標を計算
                    num_bboxes = len(past_info[tracking_id]['bboxes'])
                    x1_smooth = int(sum(b[0] for b in past_info[tracking_id]['bboxes']) / num_bboxes)
                    y1_smooth = int(sum(b[1] for b in past_info[tracking_id]['bboxes']) / num_bboxes)
                    x2_smooth = int(sum(b[2] for b in past_info[tracking_id]['bboxes']) / num_bboxes)
                    y2_smooth = int(sum(b[3] for b in past_info[tracking_id]['bboxes']) / num_bboxes)

                    # 現在のConfidenceが低い場合、過去の高いConfidenceのクラス名を使用
                    if confidence < confidence_threshold:
                        # 過去のConfidenceが高いクラス名を取得
                        max_confidence = max(past_info[tracking_id]['confidences'])
                        max_index = past_info[tracking_id]['confidences'].index(max_confidence)
                        class_name = past_info[tracking_id]['class_names'][max_index]
                else:
                    # トラッキングIDがない場合は現在の座標とクラス名を使用
                    x1_smooth, y1_smooth, x2_smooth, y2_smooth = x1, y1, x2, y2

                if y1_smooth - 5 < 0:
                    y1_smooth += 15

                # バウンディングボックスを描画
                cv2.line(frame, (x1_smooth, y1_smooth), (x2_smooth, y1_smooth), color, 2)

                # ラベルを描画
                label_text = f"{class_name} cofidence:{confidence:.2f}"
                cv2.putText(
                    frame,
                    label_text,
                    (x1_smooth, y1_smooth - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1,
                    cv2.LINE_AA
                )

        out.write(frame)

        if display_window_while_processing:
            cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # 音声を含めて動画を保存
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            tmp_output_path,
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
            output_path,
        ]
    )

    os.remove(tmp_output_path)


if __name__ == "__main__":
    annotate_video(input_video_path, output_path)