"""
Solutions PM - Configuration
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Detect serverless environment (Vercel)
IS_VERCEL = os.environ.get("VERCEL", "") != ""

# Database — on Vercel use /tmp (only writable dir); locally use data/
if IS_VERCEL:
    DB_PATH = "/tmp/onboarding.db"
else:
    DB_PATH = os.path.join(BASE_DIR, "data", "onboarding.db")

# Documents
TEMPLATES_DIR = os.path.join(BASE_DIR, "documents", "templates")
if IS_VERCEL:
    GENERATED_DIR = "/tmp/generated_docs"
else:
    GENERATED_DIR = os.path.join(BASE_DIR, "documents", "generated")

# Email (SendGrid)
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "kelvinrabbles@gmail.com")

# Flask
SECRET_KEY = os.environ.get("SECRET_KEY", "solutions-pm-dev-key-2026")
DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5050))
