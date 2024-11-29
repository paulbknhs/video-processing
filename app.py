#!/usr/bin/env python3
from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename
from datetime import datetime
import time

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "processed"

# Ensure upload and output directories exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_filename = f"normalized_{timestamp}.mp4"
    output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)

    # Normalize audio using FFmpeg
    subprocess.run(["ffmpeg", "-i", input_path, "-af", "loudnorm", output_path])

    # Provide download URL
    return jsonify({
        "download_url": f"/download/{output_filename}?t={int(time.time())}"
    }), 200

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(
        app.config["OUTPUT_FOLDER"], filename, as_attachment=True
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
