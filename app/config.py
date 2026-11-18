import os

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_PHOTOS = 3

# Days allowed to resolve a complaint before it's flagged overdue
SLA_DAYS = {
    "ROAD": 7,
    "STREETLIGHT": 3,
    "WATER_LEAKAGE": 2,
    "DRAINAGE": 3,
    "OTHER": 7,
}
