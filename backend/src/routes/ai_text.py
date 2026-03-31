from flask import Blueprint, jsonify, g, current_app
from werkzeug.exceptions import BadRequest, InternalServerError
from bson import ObjectId

from keycloak_client import require_auth
from common.python import db
from config import DB_NAME, COL_CRON_TASKS, COL_ANALYSIS_AI_TEXT
from utils import extract_request_text

ai_text_bp = Blueprint("ai", __name__)

@ai_text_bp.route("/", methods=["POST"])
@require_auth
def create_analysis():
    text = extract_request_text()

    if not text:
        raise BadRequest("No text or file provided for analysis.")

    result = db.get_database(DB_NAME)[COL_CRON_TASKS].insert_one({
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


@ai_text_bp.route("/<task_id>", methods=["GET"])
@require_auth
def get_analysis(task_id):
    task = db.get_database(DB_NAME)[COL_CRON_TASKS].find_one({"_id": ObjectId(task_id)})

    if not task:
        return jsonify({
            "success": False,
            "message": "Task not found."
        })
    
    analysis_id = task.get("return_value")

    if analysis_id is None:
        return jsonify({
            "success": False,
            "message": "Task is not completed yet."
        })

    analysis_data = db.get_database(DB_NAME)[COL_ANALYSIS_AI_TEXT].find_one({"_id": analysis_id})

    if not analysis_data:
        return jsonify({
            "success": False,
            "message": "Analysis not found."
        })

    return jsonify({
        "success": True,
        "data": {
            "text": analysis_data.get("text"),
            "ai_probability": analysis_data.get("ai_probability"),
            "segments": analysis_data.get("segments"),
            "overall": analysis_data.get("overall"),
            "user_id": analysis_data.get("user_id")
        }
    })


@ai_text_bp.route("/predictions", methods=["GET"])
@require_auth
def get_ai_predictions():
    """Return history of AI detection analyses for given user."""
    user_id = g.user.get("sub")
    if not user_id:
        raise BadRequest("User not authenticated")

    try:
        database = db.get_database(DB_NAME)
        collection = database[COL_ANALYSIS_AI_TEXT]

        cursor = collection.find({"user_id": user_id}).sort("_id", -1)

        results = [
            {
                "id": str(doc.get("_id")),
                "text": doc.get("text"),
                "ai_probability": doc.get("ai_probability"),
                "human_probability": 100 - doc.get("ai_probability", 0),
                "created_at": doc.get("timestamp"),
                "segments": doc.get("segments"),
                "overall": doc.get("overall"),
                "confidence": doc.get("overall", {}).get("confidence"),
                "type": "text",
            }
            for doc in cursor
        ]

        # results = []
        # for doc in cursor:
        #     created_at = (
        #             doc.get("timestamp")
        #             or doc.get("created_at")
        #             or getattr(doc.get("_id"), "generation_time", None)
        #     )
        #
        #     results.append({
        #         "id": str(doc.get("_id")),
        #         "text": doc.get("text"),
        #         "result": doc.get("result"),
        #         "user_id": doc.get("user_id"),
        #         "created_at": created_at,
        #         "type": "manipulation",
        #     })

        return jsonify(results)
    except Exception as e:
        current_app.logger.exception("Failed to fetch AI analyses for user %s: %s", user_id, e)
        raise InternalServerError("Failed to fetch AI analyses")