from flask import Flask, request, jsonify, send_from_directory, render_template
import cv2
from ultralytics import YOLO
import subprocess
import os
import sys
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")
app.config["UPLOAD_FOLDER"] = "./uploads"
app.config["OUTPUT_FOLDER"] = "./public"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

# import ../src/movie_detector.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from src.movie_detector import annotate_video

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_video():
    if "video" not in request.files:
        return jsonify({"message": "動画ファイルが見つかりませんでした。"}), 400
    
    file = request.files["video"]
    video_path = os.path.join(app.config["UPLOAD_FOLDER"], "input.mp4")
    file.save(video_path)
    
    # output_path = os.path.join(app.config["UPLOAD_FOLDER"], "tmp.mp4")
    final_output_path = os.path.join(app.config["OUTPUT_FOLDER"], "output.mp4")

    try:
        annotate_video(video_path, final_output_path)
        
    except Exception as e:
        logger.warning(f"An error occurred: {str(e)}")
        return jsonify({"message": f"エラーが発生しました: {str(e)}"}), 500
    
    return jsonify({
        "message": "動画が正常にアップロードされ、処理が完了しました。",
        "output_url": f"/public/output.mp4"
    })

@app.route('/public/<path:filename>')
def public_files(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


if __name__ == "__main__":
    app.run(debug=True)
