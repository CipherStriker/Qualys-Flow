import os
from pathlib import Path


BASE_URL = os.getenv("QUALYS_BASE_URL", "https://qualysapi.qg2.apps.qualys.com")
CSV_TEMPLATE_ID = os.getenv("CSV_TEMPLATE_ID", "2431093")
PDF_TEMPLATE_ID = os.getenv("PDF_TEMPLATE_ID", "2369507")

""" /project/qualys/report
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_STORAGE_PATH = os.getenv(
    "REPORT_STORAGE_PATH",
    os.path.join(BASE_DIR, "reports")
)
os.makedirs(REPORT_STORAGE_PATH, exist_ok=True)
"""

# /project/report
QUALYS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = QUALYS_DIR.parent

DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports"

REPORT_STORAGE_PATH = Path(
    os.getenv("REPORT_STORAGE_PATH", DEFAULT_REPORT_PATH)
)

REPORT_STORAGE_PATH.mkdir(exist_ok=True)