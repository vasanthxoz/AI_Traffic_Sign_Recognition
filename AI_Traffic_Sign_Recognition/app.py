"""
app.py - Flask web interface
Run:  python app.py      then open  http://127.0.0.1:5000
"""
import os
import uuid

from flask import Flask, jsonify, render_template, request, send_from_directory, url_for
from PIL import Image, UnidentifiedImageError

import config
import pipeline
from kb import KnowledgeBase
from recognition import ImageRecognizer

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
os.makedirs(config.UPLOAD_DIR, exist_ok=True)

KB = KnowledgeBase()
RECOGNIZER = ImageRecognizer(KB)
ALLOWED = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recognize", methods=["POST"])
def recognize():
    f = request.files.get("image")
    if not f or not f.filename:
        return render_template("index.html", error="Please choose an image file."), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED:
        return render_template("index.html", error="Unsupported file type. Use JPG, PNG, BMP or WEBP."), 400
    name = uuid.uuid4().hex[:12] + ext
    path = os.path.join(config.UPLOAD_DIR, name)
    f.save(path)
    try:
        result = pipeline.identify(Image.open(path), KB, RECOGNIZER)
    except (UnidentifiedImageError, OSError):
        os.remove(path)
        return render_template("index.html", error="That file is not a valid image."), 400
    return render_template("result.html", r=result, input_url=url_for("static", filename="uploads/" + name))


@app.route("/api/recognize", methods=["POST"])
def api_recognize():
    f = request.files.get("image")
    if not f:
        return jsonify(error="send an image in form field 'image'"), 400
    try:
        return jsonify(pipeline.identify(Image.open(f.stream), KB, RECOGNIZER))
    except (UnidentifiedImageError, OSError):
        return jsonify(error="invalid image"), 400


@app.route("/reference/<path:name>")
def reference_file(name):
    return send_from_directory(config.REFERENCE_DIR, name)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
