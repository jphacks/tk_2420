# Sample code to track objects in a video using YOLO11
# NOTE: movie_detector.py is a more complete version of this code
import cv2
import logging


from ultralytics import YOLO

logger = logging.getLogger(__name__)

# Load the YOLO11 model
# model = YOLO("yolo11n.pt")
model = YOLO("../hackv3i.pt")

# Open the video file
video_path = "../Whiplash.mp4"
cap = cv2.VideoCapture(video_path)

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO11 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True)
        logger.warning(results)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLO11 Tracking", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()