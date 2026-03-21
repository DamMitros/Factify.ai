from flask import Blueprint, jsonify, request, current_app, g
from werkzeug.exceptions import BadRequest, InternalServerError

from keycloak_client import require_auth
from common.python.text_extractor import extract_text
from common.python import db
from config import DB_NAME, COL_CRON_TASKS, COL_ANALYSIS_AI_TEXT, COL_ANALYSIS_MANIPULATION, COL_ANALYSIS_SOURCES

from bson.objectid import ObjectId

analysis = Blueprint("analysis", __name__)

# Podział odpowiednio na analize tekstową i obrazową, manipulacje i wyszukiwanie źródeł????
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


@analysis.route("/ai", methods=["POST"])
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


@analysis.route("/ai/<task_id>", methods=["GET"])
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


@analysis.route("/ai/predictions", methods=["GET"])
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
        current_app.logger.exception("Failed to fetch manipulation analyses for user %s: %s", user_id, e)
        raise InternalServerError("Failed to fetch manipulation analyses")


@analysis.route("/manipulation", methods=["POST"])
@require_auth
def create_manipulation_analysis():
    text = extract_request_text()

    if not text:
        raise BadRequest("No text or file provided for analysis.")

    result = db.get_database(DB_NAME)[COL_CRON_TASKS].insert_one({
        "name": "analyze_manipulation",
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


@analysis.route("/manipulation/<task_id>", methods=["GET"])
@require_auth
def get_manipulation_analysis(task_id):
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

    analysis_data = db.get_database(DB_NAME)[COL_ANALYSIS_MANIPULATION].find_one({"_id": analysis_id})

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


@analysis.route("/manipulation/predictions", methods=["GET"])
@require_auth
def get_manipulation_predictions():
    """Return history of manipulation analyses for given user."""
    user_id = g.user.get("sub")
    if not user_id:
        raise BadRequest("User not authenticated")

    try:
        database = db.get_database(DB_NAME)
        collection = database[COL_ANALYSIS_MANIPULATION]

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
                "type": "manipulation",
            })

        return jsonify(results)
    except Exception as e:
        current_app.logger.exception("Failed to fetch manipulation analyses for user %s: %s", user_id, e)
        raise InternalServerError("Failed to fetch manipulation analyses")


@analysis.route("/find_sources/predictions", methods=["GET"])
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


@analysis.route("/find_sources", methods=["POST"])
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


@analysis.route("/find_sources/<task_id>", methods=["GET"])
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
