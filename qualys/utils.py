import os
from datetime import datetime
from .config import REPORT_STORAGE_PATH

def get_target_directory(client_name):
    now = datetime.now()
    year = now.strftime("%Y")
    month_year = now.strftime("%Y-%m")

    path = os.path.join(
        REPORT_STORAGE_PATH,
        year,
        client_name,
        month_year
    )

    os.makedirs(path, exist_ok=True)
    return path


def sanitize_filename(title):
    return title.replace("/", "-").replace("\\", "-")
