from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.exceptions import BadRequest, InternalServerError
from bson import ObjectId
import base64

from common.python import db
from keycloak_client import require_auth, require_auth_optional, role_required
from config import DB_NAME, COL_CRON_TASKS, COL_ANALYSIS_AI_IMAGE

image_bp = Blueprint("image", __name__)

@image_bp.route("/detect", methods=["POST"])
@require_auth_optional
def detect_ai_image():
    if "file" not in request.files:
        raise BadRequest("No file part in the request. Please use 'file' field.")
    
    file = request.files["file"]
    
    if file.filename == "":
        raise BadRequest("No file selected for uploading.")
    
    try:
        contents = file.read()
        encoded_image = base64.b64encode(contents).decode("utf-8")
        user_id = g.user.get("sub") if g.user else None

        result = db.get_database(DB_NAME)[COL_CRON_TASKS].insert_one({
            "name": "analyze_image",
            "payload": {
                "filename": file.filename,
                "image_base64": encoded_image,
                "user_id": user_id,
            },
            "status": "scheduled"
        })

        return jsonify({
            "success": True,
            "taskId": str(result.inserted_id)
        })
    except Exception as e:
        current_app.logger.exception(f"Error queuing image for analysis: {str(e)}")
        raise InternalServerError("Failed to create analysis task.")

@image_bp.route("/detect/<task_id>", methods=["GET"])
@require_auth_optional
def get_image_analysis(task_id):
    task = db.get_database(DB_NAME)[COL_CRON_TASKS].find_one({"_id": ObjectId(task_id)})

    if not task:
        return jsonify({"success": False, "message": "Task not found."})
    
    analysis_id = task.get("return_value")

    if analysis_id is None:
        return jsonify({"success": False, "message": "Task is not completed yet."})

    analysis_data = db.get_database(DB_NAME)[COL_ANALYSIS_AI_IMAGE].find_one({"_id": analysis_id})

    if not analysis_data:
        return jsonify({"success": False, "message": "Analysis not found."})

    return jsonify({
        "success": True,
        "filename": analysis_data.get("filename"),
        "predictions": analysis_data.get("raw_predictions"),
        "is_ai": analysis_data.get("overall", {}).get("label") == "AI",
        "confidence": analysis_data.get("overall", {}).get("confidence"),
        "image_preview": analysis_data.get("image_preview")
    })

@image_bp.route("/predictions", methods=["GET"])
@require_auth
def get_image_predictions():
    user_id = g.user.get("sub")
    if not user_id:
        raise BadRequest("User not authenticated")

    try:
        database = db.get_database(DB_NAME)
        collection = database[COL_ANALYSIS_AI_IMAGE]

        cursor = collection.find({"user_id": user_id}).sort("timestamp", -1)

        results = [
            {
                "id": str(doc.get("_id")),
                "filename": doc.get("filename"),
                "ai_probability": doc.get("ai_probability"),
                "human_probability": 100 - doc.get("ai_probability", 0),
                "created_at": doc.get("timestamp"),
                "image_preview": doc.get("image_preview"),
                "overall": doc.get("overall"),
                "confidence": doc.get("overall", {}).get("confidence"),
                "type": "image"
            }
            for doc in cursor
        ]

        return jsonify(results)
    except Exception as e:
        current_app.logger.exception("Failed to fetch image predictions for user %s: %s", user_id, e)
        raise InternalServerError("Failed to fetch image predictions")

@image_bp.route("/predictions/<user_id>", methods=["GET"])
@role_required("admin")
def get_image_predictions_for_user(user_id):
    try:
        database = db.get_database(DB_NAME)
        collection = database[COL_ANALYSIS_AI_IMAGE]

        cursor = collection.find({"user_id": user_id}).sort("timestamp", -1)

        results = [
            {
                "id": str(doc.get("_id")),
                "filename": doc.get("filename"),
                "ai_probability": doc.get("ai_probability"),
                "human_probability": 100 - doc.get("ai_probability", 0),
                "created_at": doc.get("timestamp"),
                "image_preview": doc.get("image_preview"),
                "overall": doc.get("overall"),
                "confidence": doc.get("overall", {}).get("confidence"),
                "type": "image"
            }
            for doc in cursor
        ]

        return jsonify(results)
    except Exception as e:
        current_app.logger.exception("Failed to fetch image predictions for user %s: %s", user_id, e)
        raise InternalServerError("Failed to fetch image predictions for user")
    
@image_bp.route("/predictions/all_users", methods=["GET"])
@role_required("admin")
def get_image_predictions_all_users():
    try:
        database = db.get_database(DB_NAME)
        collection = database[COL_ANALYSIS_AI_IMAGE]

        cursor = collection.find().sort("timestamp", -1)

        results = [
            {
                "id": str(doc.get("_id")),
                "filename": doc.get("filename"),
                "ai_probability": doc.get("ai_probability"),
                "human_probability": 100 - doc.get("ai_probability", 0),
                "created_at": doc.get("timestamp"),
                "image_preview": doc.get("image_preview"),
                "overall": doc.get("overall"),
                "confidence": doc.get("overall", {}).get("confidence"),
                "type": "image"
            }
            for doc in cursor
        ]

        return jsonify(results)
    except Exception as e:
        current_app.logger.exception("Failed to fetch image predictions for all users: %s", e)
        raise InternalServerError("Failed to fetch image predictions for all users")
    