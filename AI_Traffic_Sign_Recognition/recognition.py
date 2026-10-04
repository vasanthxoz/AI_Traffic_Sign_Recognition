"""
recognition.py - Image recognition by reference-image (template) matching
-------------------------------------------------------------------------
No YOLO, no deep learning, no object detection, and no edge / contour /
colour-segmentation processing.  The input image is compared directly with
the stored reference image of every sign in the knowledge base:

  1. A sign can appear at any size or position in the photo, so the input is
     looked at through a set of square "windows" (9 sizes x a grid of
     positions).
  2. Every window is shrunk to 32 x 32 pixels and its raw RGB values are
     turned into a feature vector (circular centre area only, so the
     background corners do not disturb the match).  Vectors are normalised
     (mean removed, length 1) which makes the match robust to brightness.
  3. Similarity = cosine similarity (normalised cross-correlation) between a
     window vector and a reference-image vector.
  4. For every sign the best window is kept; the sign with the highest
     similarity is the recognised sign.  The similarity (in %) is the
     recognition confidence.
"""
import os

import numpy as np
from PIL import Image

import config

N = config.SIGNATURE_SIZE
_yy, _xx = np.mgrid[0:N, 0:N]
MASK = (((_xx - (N - 1) / 2) ** 2 + (_yy - (N - 1) / 2) ** 2) <= (N * 0.5) ** 2).astype(np.float32)
MASK3 = np.repeat(MASK[:, :, None], 3, axis=2).ravel()
WINDOW_SCALES = (1.0, 0.92, 0.85, 0.78, 0.71, 0.64, 0.57, 0.5, 0.44)
GRID = 9


def _vector(img):
    """32x32 RGB image -> normalised feature vector (centre circle only)."""
    v = np.asarray(img.resize((N, N), Image.BILINEAR), dtype=np.float32).ravel()
    m = (v * MASK3).sum() / MASK3.sum() / 1.0
    v = (v - m) * MASK3
    n = np.linalg.norm(v)
    return v / n if n else v


def window_vectors(image):
    """Feature vectors of all candidate windows of the input image."""
    image = image.convert("RGB")
    w, h = image.size
    side = min(w, h)
    vecs = []
    for k in WINDOW_SCALES:
        win = int(side * k)
        xs = np.linspace(0, w - win, GRID if w > win else 1).astype(int)
        ys = np.linspace(0, h - win, GRID if h > win else 1).astype(int)
        for y in ys:
            for x in xs:
                vecs.append(_vector(image.crop((x, y, x + win, y + win))))
    return np.stack(vecs)


class ImageRecognizer:
    def __init__(self, kb, ref_dir=config.REFERENCE_DIR):
        self.ids, vecs = [], []
        for sid, s in kb.signs.items():
            path = os.path.join(ref_dir, s["image"])
            if os.path.exists(path):
                self.ids.append(sid)
                vecs.append(_vector(Image.open(path).convert("RGB")))
        self.matrix = np.stack(vecs)

    def match(self, image, top_k=5):
        """Return [(sign_id, similarity_percent), ...] best first."""
        sims = (window_vectors(image) @ self.matrix.T).max(axis=0)   # best window per sign
        order = np.argsort(-sims)[:top_k]
        return [(self.ids[i], round(max(0.0, float(sims[i])) * 100, 1)) for i in order]
