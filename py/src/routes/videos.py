import logging
import os
import shutil
import uuid

import cv2
from env import MODELS_DIR, OVERLAY_URL_PREFIX, PROCESSED_DATA_DIR, UPLOADS_DIR, VIDEO_URL_PREFIX
from flask import Blueprint, jsonify, request, send_from_directory
from models import VideoInfo, db
from services.create_overlay.movie_detector import annotate_video
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


# Blueprintの初期化
videos_bp = Blueprint("videos", __name__, url_prefix=VIDEO_URL_PREFIX)

PROCESSED_VIDEO_DIR = os.path.join(PROCESSED_DATA_DIR, "videos")
PROCESSED_OVERLAY_DIR = os.path.join(PROCESSED_DATA_DIR, "overlays")


@videos_bp.route("/file/<path:filename>", methods=["GET"], strict_slashes=False)
def serve_video(filename):
    logger.info("Serve video file.")
    """動画ファイルを返す"""
    return send_from_directory(PROCESSED_VIDEO_DIR, filename)


@videos_bp.route("/list", methods=["GET"], strict_slashes=False)
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


@videos_bp.route("/<video_id>", methods=["GET"])
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


# TODO: move to a different file.
def get_video_dimensions(video_path: str):
    """Get the width and height of the video file in pixels."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return jsonify({"error": "Could not open video file"}), 500
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return (video_width, video_height)


@videos_bp.route("/upload/mp4", methods=["POST"], strict_slashes=False)
def upload_video():
    """When new video is uploaded, save the video file and create overlay data."""
    logger.info("mp4 video uploaded.")

    title = request.form.get("title")
    group_name = request.form.get("group_name")
    video_file = request.files.get("video")

    if not title or not group_name or not video_file:
        return jsonify({"error": "Missing required fields"}), 400

    video_id = str(uuid.uuid4())
    clean_title = secure_filename(title) or "video"
    video_filename = f"{clean_title}_{video_id}.mp4"

    uploaded_video_path = os.path.join(UPLOADS_DIR, "videos", video_filename)
    video_file.save(uploaded_video_path)

    video_width, video_height = get_video_dimensions(uploaded_video_path)

    # Annotate the video (add bounding boxes and overlay data)
    overlay_path = f"{PROCESSED_OVERLAY_DIR}/overlay_{video_id}.json"
    output_path = f"{PROCESSED_DATA_DIR}/videos_with_nametags/{video_filename}.mp4"
    model_path = f"{MODELS_DIR}/YOLOv11/{group_name}/hackv11i.pt"
    annotate_video(uploaded_video_path, output_path, overlay_path, model_path)

    # TODO: FIX ME.
    annotation_successful = True
    if annotation_successful:
        shutil.move(uploaded_video_path, f"{PROCESSED_VIDEO_DIR}/{video_filename}")

    # NOTE: 実際にファイルを保存するパスとリクエストを投げるパスは違う.
    new_video = VideoInfo(
        id=video_id,
        title=title,
        group_name=group_name,
        video_url=f"{VIDEO_URL_PREFIX}/file/{video_filename}",
        overlay_url=f"{OVERLAY_URL_PREFIX}/file/overlay_{video_id}.json",
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
            "video_url": new_video.video_url,
            "overlay_url": new_video.overlay_url,
            "original_video_width": new_video.original_video_width,
            "original_video_height": new_video.original_video_height,
        }
    ), 201
