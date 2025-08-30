from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from app.pdf_process import extract_info_from_pdf 

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "static/results"
UPLOAD_ORIGINAL_FOLDER = "static/uploads"
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_ORIGINAL_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    pdf_file = request.files.get("pdf_file")
    if not pdf_file or pdf_file.filename == "":
        flash("Vui lòng chọn một file PDF.")
        return redirect(url_for("index"))

    if not pdf_file.filename.lower().endswith(".pdf"):
        flash("File không đúng định dạng PDF.")
        return redirect(url_for("index"))

    # Kiểm tra dung lượng
    pdf_file.seek(0, os.SEEK_END)
    if pdf_file.tell() > MAX_FILE_SIZE_BYTES:
        flash(f"Dung lượng file vượt quá {MAX_FILE_SIZE_MB}MB.")
        return redirect(url_for("index"))
    pdf_file.seek(0)

    # Lưu file tạm vào session
    safe_filename = secure_filename(pdf_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_pdf_name = f"{os.path.splitext(safe_filename)[0]}_{timestamp}.pdf"
    saved_pdf_path = os.path.join(UPLOAD_ORIGINAL_FOLDER, saved_pdf_name)
    pdf_file.save(saved_pdf_path)

    session["upload_pdf_path"] = saved_pdf_path
    session["upload_pdf_name"] = saved_pdf_name

    return redirect(url_for("loading"))


@app.route("/loading")
def loading():
    return render_template("loading.html", next_url=url_for("result"))

@app.route("/process")
def process():
    saved_pdf_path = session.get("upload_pdf_path")
    if not saved_pdf_path or not os.path.exists(saved_pdf_path):
        return {"error": "Không tìm thấy file để xử lý"}, 400

    json_data, text = extract_info_from_pdf(saved_pdf_path)

    json_name = f"{os.path.splitext(session['upload_pdf_name'])[0]}_structured.json"
    json_path = os.path.join(UPLOAD_FOLDER, json_name)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    raw_text_path = json_path.replace(".json", "_text.txt")
    with open(raw_text_path, "w", encoding="utf-8") as f:
        f.write(text)

    return jsonify({
        "status": "done",
        "json_file": json_name
    })

@app.route("/result")
def result():
    json_file = request.args.get("file")
    if not json_file:
        flash("Thiếu tên file.")
        return redirect(url_for("index"))

    json_path = os.path.join("static/results", json_file)
    raw_text_path = json_path.replace(".json", "_text.txt")

    if not os.path.exists(json_path):
        flash("Không tìm thấy file kết quả.")
        return redirect(url_for("index"))

    try:
        with open(json_path, encoding="utf-8") as f:
            json_result = f.read()
            data_dict = json.loads(json_result)

        with open(raw_text_path, encoding="utf-8") as f:
            raw_text = f.read()

    except Exception as e:
        print("❌", e)
        flash("Không thể đọc file.")
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        json_result=json_result,
        raw_text=raw_text,
        download_link=f"results/{json_file}",
        field_count=len(data_dict)
    )

@app.template_filter("from_json")
def from_json_filter(s):
    try:
        return json.loads(s)
    except:
        return {}

if __name__ == "__main__":
    app.run(debug=True)