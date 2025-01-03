#!/usr/bin/env python3
from flask import Flask, request, render_template, send_from_directory, jsonify, url_for
import os
import subprocess
import threading
from werkzeug.utils import secure_filename
from datetime import datetime
import time
import glob
from pathlib import Path

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "processed"

# Ensure upload and output directories exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

processing_progress = {"progress": 0}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"mp4"}

def get_file_duration(file_path):
    """Get the duration of a media file in seconds using FFprobe."""
    command = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except Exception:
        return None  # Return None if duration cannot be determined

def run_ffmpeg(input_path, output_path):
    """Run FFmpeg and update progress."""
    global processing_progress
    total_duration = get_file_duration(input_path)
    if total_duration is None:
        total_duration = 1  # Avoid division by zero; fallback value

    command = [
        "ffmpeg", "-i", input_path, "-af", "loudnorm",
        "-progress", "-", "-nostats", output_path
    ]
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    for line in process.stdout:
        if "out_time_ms" in line:
            try:
                # Parse progress and calculate percentage
                time_ms = int(line.split("=")[1].strip())
                current_time = time_ms / 1000000  # Convert microseconds to seconds
                progress = min(int((current_time / total_duration) * 100), 100)
                processing_progress["progress"] = progress
            except ValueError:
                pass

    process.wait()
    processing_progress["progress"] = 100  # Ensure progress is marked complete

def get_processed_files():
    """Get list of processed files with their metadata."""
    files = []
    for file_path in glob.glob(os.path.join(app.config["OUTPUT_FOLDER"], "*.mp4")):
        path = Path(file_path)
        files.append({
            'filename': path.name,
            'timestamp': datetime.fromtimestamp(path.stat().st_mtime),
            'thumbnail_url': url_for('get_thumbnail', filename=path.name)
        })
    # Sortiere nach Zeitstempel, neueste zuerst
    return sorted(files, key=lambda x: x['timestamp'], reverse=True)

def generate_thumbnail(video_path, thumbnail_path):
    """Generate thumbnail for video file."""
    command = [
        "ffmpeg", "-i", video_path,
        "-ss", "00:00:01",  # Nimm Frame nach 1 Sekunde
        "-vframes", "1",
        "-vf", "scale=120:-1",  # Thumbnail Breite: 120px, Höhe proportional
        thumbnail_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@app.route("/")
def index():
    """Render the index page with list of processed files."""
    processed_files = get_processed_files()
    return render_template("index.html", processed_files=processed_files)

@app.route("/thumbnail/<filename>")
def get_thumbnail(filename):
    """Serve video thumbnail."""
    video_path = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    thumbnail_dir = os.path.join(app.config["OUTPUT_FOLDER"], "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    thumbnail_filename = f"{Path(filename).stem}_thumb.jpg"
    thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
    
    # Generiere Thumbnail wenn es noch nicht existiert
    if not os.path.exists(thumbnail_path):
        generate_thumbnail(video_path, thumbnail_path)
    
    return send_from_directory(thumbnail_dir, thumbnail_filename)

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload and start FFmpeg processing."""
    global processing_progress

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only MP4 files are allowed."}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    # Generate timestamped output filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_filename = f"normalized_{timestamp}.mp4"
    output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)

    # Reset progress
    processing_progress = {"progress": 0}

    # Start FFmpeg processing in a thread
    thread = threading.Thread(target=run_ffmpeg, args=(input_path, output_path))
    thread.start()
    thread.join()  # Wait for the thread to complete

    # Provide download URL
    return jsonify({
        "download_url": url_for("download_file", filename=output_filename, _external=True)
    }), 200

@app.route("/processing-progress", methods=["GET"])
def get_progress():
    """Return the current processing progress."""
    return jsonify(processing_progress)

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """Allow downloading the processed file."""
    return send_from_directory(
        app.config["OUTPUT_FOLDER"], filename, as_attachment=True
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
