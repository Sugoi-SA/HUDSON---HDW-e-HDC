import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
STORAGE_ROOT = os.environ["STORAGE_ROOT"]
API_KEY = os.environ["API_KEY"]
API_KEY_SERVIDOR = os.environ.get("API_KEY_SERVIDOR")

TESSERACT_CMD = os.environ.get("TESSERACT_CMD") or None
POPPLER_PATH = os.environ.get("POPPLER_PATH") or None
