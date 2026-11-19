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
APP_URL = os.getenv("APP_URL", "http://127.0.0.1:8000")
REQUIRE_EMAIL_VERIFICATION = os.getenv("REQUIRE_EMAIL_VERIFICATION", "true").lower() == "true"
CODE_TTL_MINUTES = 15
CODE_MAX_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60

# Emails go through Brevo's web API. With no key set, emails are printed in the terminal instead.
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
MAIL_FROM_EMAIL = os.getenv("MAIL_FROM_EMAIL", "")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "FixMyCity")