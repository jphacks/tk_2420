from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import uuid
import cv2
from werkzeug.utils import secure_filename
from movie_detector import annotate_video
from models import db, VideoInfo  # models からインポート

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///video_info.db"
CORS(app, origins=["http://localhost:3000"])  # Allow requests from React app.

# dbの初期化
db.init_app(app)

# Base directories for video and overlay files
VIDEO_DIR = "videos"
OVERLAY_DIR = "overlays"

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
def create_overlay(video_path, video_id: str) -> str:
    """Creates overlay data in JSON for the given video file using its unique ID."""
    overlay_json_path = f"{OVERLAY_DIR}/overlay_{video_id}.json"
    mp4_output_path = os.path.join("overlay_movie", f"overlay_{video_id}.mp4")
    annotate_video(video_path, mp4_output_path, overlay_json_path)
    return overlay_json_path


def get_video_dimensions(video_path: str):
    """Get the width and height of the video file in pixels."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return jsonify({"error": "Could not open video file"}), 500
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return (video_width, video_height)


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
    clean_title = secure_filename(title)
    if not clean_title:
        clean_title = "video"

    video_filename = f"{clean_title}_{video_id}.mp4"
    video_path = os.path.join(VIDEO_DIR, video_filename)
    video_file.save(video_path)

    video_width, video_height = get_video_dimensions(video_path)
    overlay_path = create_overlay(video_path, video_id)

    new_video = VideoInfo(
        id=video_id,
        title=title,
        group_name=group_name,
        video_url=video_path,
        overlay_url=overlay_path,
        original_video_width=video_width,
        original_video_height=video_height,
    )
    db.session.add(new_video)
    db.session.commit()

    return jsonify(
        {
            "id": new_video.id,
            "title": new_video.title,
            "group_name": new_video.group_name,
            "video_url": f"/{new_video.video_url}",
            "overlay_url": new_video.overlay_url,
            "original_video_width": new_video.original_video_width,
            "original_video_height": new_video.original_video_height,
        }
    ), 201


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
