import os

from env import MODELS_DIR, OVERLAY_URL_PREFIX, PROCESSED_DATA_DIR
from flask import Blueprint, jsonify, request, send_from_directory
from services.create_overlay.movie_detector import annotate_video

# Blueprintの初期化
overlays_bp = Blueprint("overlays", __name__, url_prefix=OVERLAY_URL_PREFIX)

PROCESSED_OVERLAY_DIR = os.path.join(PROCESSED_DATA_DIR, "overlays")
PROCESSED_VIDEO_DIR = os.path.join(PROCESSED_DATA_DIR, "videos")


# Route to serve overlay JSON files
@overlays_bp.route("/file/<path:filename>")
def serve_overlay(filename):
    """Returns the overlay JSON file."""
    return send_from_directory(PROCESSED_OVERLAY_DIR, filename)


@overlays_bp.route("/update", methods=["POST"], strict_slashes=False)
def update_overlay():
    """Updates the overlay JSON file."""
    video_id = request.json.get("video_id")
    overlay_url = request.json.get("overlay_url")
    video_url = request.json.get("video_url")
    group_name = request.json.get("group_name")

    if not video_id:
        return jsonify({"error": "Video not found"}), 404

    video_filename = video_url.split("/")[-1]
    overlay_filename = overlay_url.split("/")[-1]

    # Locate the original file paths
    original_video_path = os.path.join(PROCESSED_VIDEO_DIR, video_filename)
    original_video_with_nametags_path = os.path.join(PROCESSED_DATA_DIR, "videos_with_nametags", video_filename)
    original_overlay_path = os.path.join(PROCESSED_OVERLAY_DIR, overlay_filename)

    if (
        not os.path.exists(original_video_path)
        or not os.path.exists(original_overlay_path)
        or not os.path.exists(original_video_with_nametags_path)
    ):
        return jsonify({"error": "Original files not found"}), 404

    TEMP_DIR = os.path.join(PROCESSED_DATA_DIR, "temp")
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Define temporary paths
    temp_video_path = os.path.join(TEMP_DIR, f"temp_{video_filename}.mp4")
    temp_overlay_path = os.path.join(TEMP_DIR, f"temp_{overlay_filename}.json")

    try:
        # Reprocess video and save to temporary files
        model_path = f"{MODELS_DIR}/YOLOv11/{group_name}/hackv11i.pt"
        annotate_video(original_video_path, temp_video_path, temp_overlay_path, model_path)

        # Replace old files with new ones atomically
        os.replace(temp_video_path, original_video_with_nametags_path)
        os.replace(temp_overlay_path, original_overlay_path)

        return jsonify({"message": "Video updated successfully"})

    except Exception as e:
        # Cleanup temporary files if something goes wrong
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if os.path.exists(temp_overlay_path):
            os.remove(temp_overlay_path)
        return jsonify({"error": str(e)}), 500
    finally:
        os.rmdir(TEMP_DIR)
