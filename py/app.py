import json
import os
import uuid

import cv2
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from models import AnnotationLabel, VideoInfo, db  # models からインポート
from movie_detector import annotate_video
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///video_info.db"
CORS(app)  # Allow requests tentatively. TODO: tighten this up

# dbの初期化
db.init_app(app)

# Base directories for video, overlay, and annotation files
VIDEO_DIR = "videos"
OVERLAY_DIR = "overlays"
ANNOTATION_DIR = "additional_dataset"

# Ensure directories exist
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(OVERLAY_DIR, exist_ok=True)
os.makedirs(ANNOTATION_DIR, exist_ok=True)


# Serve static files.
# Route to serve video files
@app.route(f"/{VIDEO_DIR}/<path:filename>")
def serve_video(filename):
    return send_from_directory("videos", filename)


# Route to serve overlay JSON files
@app.route(f"/{OVERLAY_DIR}/<path:filename>")
def serve_overlay(filename):
    return send_from_directory("overlays", filename)


@app.route("/api/videos", methods=["GET"])
def get_videos():
    """Get list of videos, optionally filtered by group_name"""
    group_name = request.args.get("group_name")
    query = db.select(VideoInfo).order_by(VideoInfo.title)
    if group_name:
        query = query.filter(VideoInfo.group_name == group_name)
    videos = db.session.execute(query).scalars().all()

    return jsonify(
        [
            {
                "id": video.id,
                "title": video.title,
                "group_name": video.group_name,
                "video_url": video.video_url,
                "overlay_url": video.overlay_url,
                "original_video_width": video.original_video_width,
                "original_video_height": video.original_video_height,
            }
            for video in videos
        ]
    )


# NOTE: This is not used by the frontend now. Consider removing this endpoint.
@app.route("/api/videos/<video_id>", methods=["GET"])
def get_video_data(video_id: str):
    """Get specific video data including overlay"""
    video = db.get_or_404(VideoInfo, video_id)

    video_data = {
        "id": video.id,
        "title": video.title,
        "group_name": video.group_name,
        "video_url": video.video_url,
        "overlay_url": video.overlay_url,
        "original_video_width": video.original_video_width,
        "original_video_height": video.original_video_height,
    }
    return jsonify(video_data)


# TODO: This should be implemented in a separate module
# TODO: This is sitll a dummy implementation. Implement the actual overlay creation logic.
def create_overlay(video_file, video_id: str) -> str:
    """Creates overlay data in JSON for the given video file using its unique ID."""
    overlay_path = f"{OVERLAY_DIR}/overlay_{video_id}.json"
    # Dummy overlay content for illustration
    overlay_data = {"data": "overlay content"}
    with open(os.path.join("overlays", f"overlay_{video_id}.json"), "w") as f:
        json.dump(overlay_data, f)
    return overlay_path


def get_video_dimensions(video_path: str):
    """Get the width and height of the video file in pixels."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return jsonify({"error": "Could not open video file"}), 500
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return (video_width, video_height)


@app.route("/api/upload_kpop_face_match", methods=["POST"])
def upload_kpop_face_match():
    dummy_data = "Winter"
    return jsonify({"idol_name": dummy_data}), 201


@app.route("/api/upload", methods=["POST"])
def upload_video():
    """When new video is uploaded, save the video file and create overlay data."""
    title = request.form.get("title")
    group_name = request.form.get("group_name")
    video_file = request.files.get("video")

    if not title or not group_name or not video_file:
        return jsonify({"error": "Missing required fields"}), 400

    video_id = str(uuid.uuid4())
    # Save the uploaded video file
    clean_title = secure_filename(title) or "video"

    video_filename = f"{clean_title}_{video_id}.mp4"
    video_path = os.path.join(VIDEO_DIR, video_filename)
    video_file.save(video_path)

    video_width, video_height = get_video_dimensions(video_path)

    # Annotate the video (add bounding boxes and overlay data)
    overlay_path = create_overlay(video_file, video_id)
    output_path = "output.mp4"
    annotate_video(video_path, output_path, overlay_path, "../hackday/models/hackv4i.pt")

    # new_video = VideoInfo(
    #     id=video_id,
    #     title=title,
    #     group_name=group_name,
    #     video_url=video_path,
    #     overlay_url=overlay_path,
    #     original_video_width=video_width,
    #     original_video_height=video_height,
    # )
    # db.session.add(new_video)
    # db.session.commit()

    return jsonify(
        {
            "id": video_id,
            "title": title,
            "group_name": group_name,
            "video_url": f"/videos/{video_filename}",
            "overlay_url": f"/overlays/overlay_{video_id}.json",
            "original_video_width": video_width,
            "original_video_height": video_height,
        }
    ), 201


@app.route("/api/upload_annotation", methods=["POST"])
def upload_annotation():
    """Upload new annotation data and save to the specified directory."""
    annotation_file = request.files.get("annotation")
    image_file = request.files.get("image")
    group_name = request.form.get("groupName")

    if not annotation_file or not image_file or not group_name:
        return jsonify({"error": "Missing annotation or image file or group name"}), 400

    group_dir = os.path.join(ANNOTATION_DIR, group_name)
    os.makedirs(group_dir, exist_ok=True)

    annotation_id = str(uuid.uuid4())

    annotation_filename = f"{annotation_id}.txt"
    annotation_path = os.path.join(group_dir, annotation_filename)
    annotation_file.save(annotation_path)

    image_filename = f"{annotation_id}.jpeg"
    image_path = os.path.join(group_dir, image_filename)
    image_file.save(image_path)

    print(f"Annotation saved to {annotation_path} and image saved to {image_path}")

    return jsonify(
        {
            "message": "Annotation and image uploaded successfully",
        }
    ), 201


@app.route("/api/annotation_labels", methods=["GET"])
def get_annotation_labels():
    """Get list of annotation labels"""
    group_name = request.args.get("groupName")
    print(f"group_name: {group_name}")

    labels = (
        db.session.execute(
            db.select(AnnotationLabel).filter_by(group_name=group_name).order_by(AnnotationLabel.label_id)
        )
        .scalars()
        .all()
    )

    # Convert to a list of dictionaries
    labels_dict = [
        {
            "label_id": label.label_id,
            "label_name": label.label_name,
            "label_color": label.label_color,
            "group_name": label.group_name,
        }
        for label in labels
    ]
    return jsonify(labels_dict)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
