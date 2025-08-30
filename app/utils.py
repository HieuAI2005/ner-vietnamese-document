import json
import os
from datetime import datetime

UPLOAD_FOLDER = "static/uploads"

def save_json_file(filename, data):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    out_name = f"{filename.rsplit('.', 1)[0]}_structured_{timestamp}.json"
    path = os.path.join(UPLOAD_FOLDER, out_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path