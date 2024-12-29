#!/usr/bin/env python3

from flask import Flask, request, render_template, send_from_directory, jsonify, url_for
import os
import subprocess
from werkzeug.utils import secure_filename
from datetime import datetime
import time

# Initialize Flask app
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "processed"
app.config["ALLOWED_EXTENSIONS"] = {"mp4"}

# Ensure upload and output directories exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

def allowed_file(filename: str) -> bool:
    """Check if a file is allowed based on its extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file uploads."""
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

    # Normalize audio using FFmpeg
    subprocess.run(["ffmpeg", "-i", input_path, "-af", "loudnorm", output_path])

    # Provide download URL
    return jsonify({
        "download_url": url_for("download_file", filename=output_filename, _external=True)
    }), 200

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename: str):
    """Serve the processed file for download."""
    return send_from_directory(
        app.config["OUTPUT_FOLDER"], filename, as_attachment=True
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
