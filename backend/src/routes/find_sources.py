from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.exceptions import BadRequest, InternalServerError
from bson import ObjectId

from keycloak_client import require_auth, role_required
from common.python import db
from config import DB_NAME, COL_CRON_TASKS, COL_ANALYSIS_SOURCES
from utils import extract_request_text

find_sources_bp = Blueprint("find_sources", __name__)

@find_sources_bp.route("/", methods=["POST"])
@require_auth
def create_find_sources_analisys():
    text = extract_request_text()

    if not text:
        raise BadRequest("No text or file provided for analysis.")

    result = db.get_database(DB_NAME)[COL_CRON_TASKS].insert_one({
        "name": "find_sources",
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


@find_sources_bp.route("/<task_id>", methods=["GET"])
@require_auth
def get_find_sources_analysis(task_id):
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

    analysis_data = db.get_database(DB_NAME)[COL_ANALYSIS_SOURCES].find_one({"_id": analysis_id})

    if not analysis_data:
        return jsonify({
            "success": False,
            "message": "Analysis not found."
        })

    return jsonify({
        "success": True,
        "data": {
            "text": analysis_data.get("text"),
            "result": analysis_data.get("result"),
            "user_id": analysis_data.get("user_id")
        }
    })

@find_sources_bp.route("/predictions", methods=["GET"])
@require_auth
def get_find_sources_predictions():
    """Return history of find_sources analyses for given user."""
    user_id = g.user.get("sub")
    if not user_id:
        raise BadRequest("User not authenticated")

    try:
        database = db.get_database(DB_NAME)
        collection = database[COL_ANALYSIS_SOURCES]

        cursor = collection.find({"user_id": user_id}).sort("_id", -1)

        results = []
        for doc in cursor:
            created_at = (
                doc.get("timestamp")
                or doc.get("created_at")
                or getattr(doc.get("_id"), "generation_time", None)
            )

            results.append({
                "id": str(doc.get("_id")),
                "text": doc.get("text"),
                "result": doc.get("result"),
                "user_id": doc.get("user_id"),
                "created_at": created_at,
                "type": "find_sources",
            })

        return jsonify(results)
    except Exception as e:
        current_app.logger.exception("Failed to fetch find_sources analyses for user %s: %s", user_id, e)
        raise InternalServerError("Failed to fetch find_sources analyses")
    
@find_sources_bp.route("/predictions/<user_id>", methods=["GET"])
@role_required("admin")
def get_find_sources_predictions_for_user(user_id):
    try:
        database = db.get_database(DB_NAME)
        collection = database[COL_ANALYSIS_SOURCES]

        cursor = collection.find({"user_id": user_id}).sort("_id", -1)

        results = []
        for doc in cursor:
            created_at = (
                doc.get("timestamp")
                or doc.get("created_at")
                or getattr(doc.get("_id"), "generation_time", None)
            )

            results.append({
                "id": str(doc.get("_id")),
                "text": doc.get("text"),
                "result": doc.get("result"),
                "user_id": doc.get("user_id"),
                "created_at": created_at,
                "type": "find_sources",
            })

        return jsonify(results)
    except Exception as e:
        current_app.logger.exception("Failed to fetch find_sources analyses for user %s: %s", user_id, e)
        raise InternalServerError("Failed to fetch find_sources analyses")
    
@find_sources_bp.route("/predictions/all_users", methods=["GET"])
@role_required("admin")
def get_find_sources_predictions_all_users():
    try:
        database = db.get_database(DB_NAME)
        collection = database[COL_ANALYSIS_SOURCES]

        cursor = collection.find().sort("_id", -1)

        results = []
        for doc in cursor:
            created_at = (
                doc.get("timestamp")
                or doc.get("created_at")
                or getattr(doc.get("_id"), "generation_time", None)
            )

            results.append({
                "id": str(doc.get("_id")),
                "text": doc.get("text"),
                "result": doc.get("result"),
                "user_id": doc.get("user_id"),
                "created_at": created_at,
                "type": "find_sources",
            })

        return jsonify(results)
    except Exception as e:
        current_app.logger.exception("Failed to fetch find_sources analyses for all users: %s", e)
        raise InternalServerError("Failed to fetch find_sources analyses")
    