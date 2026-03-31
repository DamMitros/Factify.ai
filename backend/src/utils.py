from flask import request, current_app
from werkzeug.exceptions import InternalServerError
from common.python.text_extractor import extract_text

def extract_request_text():
    if "file" in request.files:
        file = request.files["file"]

        if file.filename != "":
            try:
                return extract_text(file, filename=file.filename)
            except Exception as e:
                current_app.logger.exception(f"Text extraction failed: {e}")
                raise InternalServerError("Failed to extract text from the uploaded file.")

    json_payload = request.get_json(silent=True) or {}

    return str(json_payload.get("text", "")).strip()
