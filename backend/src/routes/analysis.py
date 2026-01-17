from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.exceptions import BadRequest, InternalServerError

from keycloak_client import require_auth
from common.python.text_extractor import extract_text
from common.python import db

analysis = Blueprint("analysis", __name__)

@analysis.route("/create", methods=["POST"])
@require_auth
def create_analysis():
    text = ""

    if "file" in request.files:
        file = request.files["file"]
        if file.filename != "":
            try:
                text = extract_text(file, filename=file.filename)
            except Exception as e:
                current_app.logger.exception(f"Text extraction failed: {e}")
                raise InternalServerError("Failed to extract text from the uploaded file.")
    else:
        json_payload = request.get_json(silent=True) or {}
        text = str(json_payload.get("text", "")).strip()

    if not text:
        raise BadRequest("No text or file provided for analysis.")

    result = db.get_database("factify")["cron_tasks"].insert_one({
        "name": "analyze",
        "payload": {
            "text": text,
            "user_id": g.user.get("sub"),
        },
        "status": "scheduled"
    })

    return jsonify({
        "success": True,
        "taskId": str(result.inserted_id)
    })
