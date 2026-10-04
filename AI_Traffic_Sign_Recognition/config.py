"""Project configuration."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REFERENCE_DIR = os.path.join(BASE_DIR, "reference_images")
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_inputs")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
DATA_DIR = os.path.join(BASE_DIR, "data")

# MongoDB (knowledge base).  If MongoDB is not running the system falls back
# to data/knowledge_base.json + data/rules.json automatically.
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "traffic_sign_db"

# Image-recognition settings
SIGNATURE_SIZE = 32          # reference/input images are compared at 32x32 pixels
MIN_CONFIDENCE = 60.0        # below this similarity (%) the sign is reported as UNKNOWN
