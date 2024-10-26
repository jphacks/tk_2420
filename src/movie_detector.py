import cv2
from ultralytics import YOLO
import subprocess
import os

video_path = "<input_movie_file_path>"
output_path = "<output_movie_file_path>"

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        results = model.predict(frame, classes=[0])  # detect only person, class id is 0
        annotated_frame = results[0].plot()
        out.write(annotated_frame)
        cv2.imshow("Frame", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()

final_output_path = "Whiplash_yolov8.mp4"
subprocess.run(
    [
        "ffmpeg",
        "-i",
        output_path,
        "-i",
        video_path,
        "-c",
        "copy",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-y",
        final_output_path,
    ]
)

os.remove(output_path)
